"""管理者用 Admin パネルのルーター。"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.admin.auth import (
    COOKIE_NAME,
    authenticate_admin,
    create_session_token,
    get_current_admin,
    hash_password,
    verify_password,
)
from app.api.admin.import_service import (
    JobParams,
    create_and_start_job,
    get_active_job,
    has_gemini_key,
)
from app.infrastructure.db.models import (
    AdminUser,
    Article,
    ArticleDisplayContent,
    ArticleEvent,
    DailyArticleStat,
    DailyCategoryStat,
    ImportJob,
    ImportJobLog,
    Party,
    PolicyCategory,
)
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

PAGE_SIZE = 20


def _redirect_with_msg(path: str, msg: str, msg_type: str = "success"):
    """メッセージ付きリダイレクトレスポンスを返す。"""
    encoded_msg = quote(msg)
    return RedirectResponse(f"{path}?msg={encoded_msg}&type={msg_type}", status_code=302)


def _split_lines(text: str) -> list[str]:
    """改行区切りのテキストを配列に変換する。"""
    return [line.strip() for line in text.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# ルート
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
def admin_root():
    return RedirectResponse("/admin/articles", status_code=302)


# ---------------------------------------------------------------------------
# 認証
# ---------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"error": None},
    )


@router.post("/login")
def login(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    # 1. 認証を試みる
    user = authenticate_admin(db, username, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"error": "ユーザー名またはパスワードが正しくありません"},
            status_code=401,
        )
    # 2. セッショントークンを生成してクッキーにセットする
    token = create_session_token(user.id)
    response = RedirectResponse("/admin/articles", status_code=302)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400 * 7,
    )
    return response


@router.post("/logout")
def logout():
    # 1. クッキーを削除してログインページへリダイレクトする
    response = RedirectResponse("/admin/login", status_code=302)
    response.delete_cookie(key=COOKIE_NAME)
    return response


@router.get("/change-password", response_class=HTMLResponse)
def change_password_page(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/change_password.html",
        context={"admin": admin},
    )


@router.post("/change-password")
def change_password(
    request: Request,
    db: Session = Depends(get_db),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 旧パスワードを検証する
        if not verify_password(current_password, admin.hashed_password):
            return _redirect_with_msg("/admin/change-password", "現在のパスワードが正しくありません", "error")
        # 3. 新パスワードの一致を確認する
        if new_password != confirm_password:
            return _redirect_with_msg("/admin/change-password", "新しいパスワードが一致しません", "error")
        # 4. パスワードを更新する
        admin.hashed_password = hash_password(new_password)
        db.commit()
        return _redirect_with_msg("/admin/change-password", "パスワードを変更しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/change-password", f"エラーが発生しました: {e}", "error")


# ---------------------------------------------------------------------------
# 記事管理
# ---------------------------------------------------------------------------

@router.get("/articles", response_class=HTMLResponse)
def articles_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 記事一覧を取得する（display_content を eager load）
    offset = (page - 1) * PAGE_SIZE
    total = db.query(Article).count()
    articles = (
        db.query(Article)
        .order_by(Article.published_at.desc())
        .offset(offset)
        .limit(PAGE_SIZE)
        .all()
    )
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    return templates.TemplateResponse(
        request=request,
        name="admin/articles/list.html",
        context={
            "articles": articles,
            "page": page,
            "total_pages": total_pages,
            "admin": admin,
        },
    )


@router.get("/articles/new", response_class=HTMLResponse)
def articles_new_page(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/articles/form.html",
        context={"article": None, "display_content": None, "admin": admin},
    )


@router.post("/articles/new")
def articles_create(
    request: Request,
    db: Session = Depends(get_db),
    original_title: str = Form(""),
    source_type: str = Form(""),
    primary_source_url: str = Form(""),
    published_at: str = Form(...),
    status: str = Form("draft"),
    important_rank: Optional[str] = Form(None),
    is_published: Optional[str] = Form(None),
    display_title: str = Form(""),
    card_summary: str = Form(""),
    thumbnail_type: str = Form("none"),
    thumbnail_text: str = Form(""),
    positive_point: str = Form(""),
    life_impact: str = Form(""),
    remaining_issues: str = Form(""),
    public_reactions_summary: str = Form(""),
    raw_content: str = Form(""),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. published_at をパースする
        dt = datetime.fromisoformat(published_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # 3. Article を作成する
        article = Article(
            original_title=original_title or None,
            source_type=source_type or None,
            primary_source_url=primary_source_url or None,
            published_at=dt,
            status=status,
            important_rank=int(important_rank) if important_rank else None,
            is_published=(is_published == "on"),
            raw_content=raw_content or None,
        )
        db.add(article)
        db.flush()
        # 4. ArticleDisplayContent を作成する
        if display_title:
            dc = ArticleDisplayContent(
                article_id=article.id,
                display_title=display_title,
                card_summary=card_summary,
                thumbnail_type=thumbnail_type or None,
                thumbnail_text=thumbnail_text or None,
                positive_point=positive_point,
                life_impact=life_impact,
                remaining_issues=remaining_issues,
                public_reactions_summary=public_reactions_summary or None,
            )
            db.add(dc)
        db.commit()
        return _redirect_with_msg("/admin/articles", "記事を作成しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/articles", f"エラーが発生しました: {e}", "error")


@router.get("/articles/{article_id}/edit", response_class=HTMLResponse)
def articles_edit_page(
    article_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 記事を取得する
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return _redirect_with_msg("/admin/articles", "記事が見つかりません", "error")
    return templates.TemplateResponse(
        request=request,
        name="admin/articles/form.html",
        context={
            "article": article,
            "display_content": article.display_content,
            "admin": admin,
        },
    )


@router.post("/articles/{article_id}/edit")
def articles_update(
    article_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    original_title: str = Form(""),
    source_type: str = Form(""),
    primary_source_url: str = Form(""),
    published_at: str = Form(...),
    status: str = Form("draft"),
    important_rank: Optional[str] = Form(None),
    is_published: Optional[str] = Form(None),
    display_title: str = Form(""),
    card_summary: str = Form(""),
    thumbnail_type: str = Form("none"),
    thumbnail_text: str = Form(""),
    positive_point: str = Form(""),
    life_impact: str = Form(""),
    remaining_issues: str = Form(""),
    public_reactions_summary: str = Form(""),
    raw_content: str = Form(""),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 記事を取得する
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return _redirect_with_msg("/admin/articles", "記事が見つかりません", "error")
        # 3. published_at をパースする
        dt = datetime.fromisoformat(published_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # 4. Article を更新する
        article.original_title = original_title or None
        article.source_type = source_type or None
        article.primary_source_url = primary_source_url or None
        article.published_at = dt
        article.status = status
        article.important_rank = int(important_rank) if important_rank else None
        article.is_published = (is_published == "on")
        article.raw_content = raw_content or None
        # 5. ArticleDisplayContent を更新または作成する
        if display_title:
            dc = article.display_content
            if dc:
                dc.display_title = display_title
                dc.card_summary = card_summary
                dc.thumbnail_type = thumbnail_type or None
                dc.thumbnail_text = thumbnail_text or None
                dc.positive_point = positive_point
                dc.life_impact = life_impact
                dc.remaining_issues = remaining_issues
                dc.public_reactions_summary = public_reactions_summary or None
            else:
                dc = ArticleDisplayContent(
                    article_id=article.id,
                    display_title=display_title,
                    card_summary=card_summary,
                    thumbnail_type=thumbnail_type or None,
                    thumbnail_text=thumbnail_text or None,
                    positive_point=positive_point,
                    life_impact=life_impact,
                    remaining_issues=remaining_issues,
                    public_reactions_summary=public_reactions_summary or None,
                )
                db.add(dc)
        db.commit()
        return _redirect_with_msg("/admin/articles", "記事を更新しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/articles", f"エラーが発生しました: {e}", "error")


@router.post("/articles/{article_id}/delete")
def articles_delete(
    article_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 記事を取得する
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return _redirect_with_msg("/admin/articles", "記事が見つかりません", "error")
        # 3. 関連レコードを先に削除する（cascade 未設定のため手動削除）
        if article.display_content:
            db.delete(article.display_content)
        for source in article.sources:
            db.delete(source)
        db.flush()
        # 4. 記事を削除する
        db.delete(article)
        db.commit()
        return _redirect_with_msg("/admin/articles", "記事を削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/articles", f"エラーが発生しました: {e}", "error")


@router.post("/articles/bulk-action")
def articles_bulk_action(
    request: Request,
    db: Session = Depends(get_db),
    action: str = Form(...),
    article_ids: list[str] = Form(default=[]),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 対象 ID が空の場合はエラー表示
    if not article_ids:
        return _redirect_with_msg("/admin/articles", "対象が選択されていません", "error")
    # 3. 有効なアクションを確認する
    if action not in ("publish", "unpublish", "draft"):
        return _redirect_with_msg("/admin/articles", "不正な操作です", "error")
    try:
        # 4. 各記事を更新する
        updated = 0
        for aid_str in article_ids:
            try:
                aid = uuid.UUID(aid_str)
            except ValueError:
                continue
            article = db.query(Article).filter(Article.id == aid).first()
            if not article:
                continue
            if action == "publish":
                article.is_published = True
                article.status = "processed"
            elif action == "unpublish":
                article.is_published = False
            elif action == "draft":
                article.is_published = False
                article.status = "draft"
            updated += 1
        db.commit()
        label = {"publish": "公開", "unpublish": "非公開", "draft": "下書き"}[action]
        return _redirect_with_msg("/admin/articles", f"{updated} 件を{label}にしました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/articles", f"エラーが発生しました: {e}", "error")


# ---------------------------------------------------------------------------
# 政党管理
# ---------------------------------------------------------------------------

@router.get("/parties", response_class=HTMLResponse)
def parties_list(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 政党一覧を取得する
    parties = db.query(Party).order_by(Party.display_order).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/parties/list.html",
        context={"parties": parties, "admin": admin},
    )


@router.get("/parties/new", response_class=HTMLResponse)
def parties_new_page(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/parties/form.html",
        context={"party": None, "admin": admin},
    )


@router.post("/parties/new")
def parties_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    short_name: str = Form(...),
    color_hex: str = Form(""),
    is_active: Optional[str] = Form(None),
    display_order: int = Form(0),
    founded_year: Optional[str] = Form(None),
    leader_name: str = Form(""),
    house_of_representatives_seats: Optional[str] = Form(None),
    house_of_councillors_seats: Optional[str] = Form(None),
    ideology_summary: str = Form(""),
    manifesto_summary: str = Form(""),
    manifesto_promises: str = Form(""),
    main_policy_categories: str = Form(""),
    official_url: str = Form(""),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 政党を作成する
        party = Party(
            name=name,
            short_name=short_name,
            color_hex=color_hex or None,
            is_active=(is_active == "on"),
            display_order=display_order,
            founded_year=int(founded_year) if founded_year else None,
            leader_name=leader_name or None,
            house_of_representatives_seats=int(house_of_representatives_seats) if house_of_representatives_seats else None,
            house_of_councillors_seats=int(house_of_councillors_seats) if house_of_councillors_seats else None,
            ideology_summary=ideology_summary or None,
            manifesto_summary=manifesto_summary or None,
            manifesto_promises=_split_lines(manifesto_promises),
            main_policy_categories=_split_lines(main_policy_categories),
            official_url=official_url or None,
        )
        db.add(party)
        db.commit()
        return _redirect_with_msg("/admin/parties", "政党を作成しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/parties", f"エラーが発生しました: {e}", "error")


@router.get("/parties/{party_id}/edit", response_class=HTMLResponse)
def parties_edit_page(
    party_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 政党を取得する
    party = db.query(Party).filter(Party.id == party_id).first()
    if not party:
        return _redirect_with_msg("/admin/parties", "政党が見つかりません", "error")
    return templates.TemplateResponse(
        request=request,
        name="admin/parties/form.html",
        context={"party": party, "admin": admin},
    )


@router.post("/parties/{party_id}/edit")
def parties_update(
    party_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    short_name: str = Form(...),
    color_hex: str = Form(""),
    is_active: Optional[str] = Form(None),
    display_order: int = Form(0),
    founded_year: Optional[str] = Form(None),
    leader_name: str = Form(""),
    house_of_representatives_seats: Optional[str] = Form(None),
    house_of_councillors_seats: Optional[str] = Form(None),
    ideology_summary: str = Form(""),
    manifesto_summary: str = Form(""),
    manifesto_promises: str = Form(""),
    main_policy_categories: str = Form(""),
    official_url: str = Form(""),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 政党を取得する
        party = db.query(Party).filter(Party.id == party_id).first()
        if not party:
            return _redirect_with_msg("/admin/parties", "政党が見つかりません", "error")
        # 3. 政党を更新する
        party.name = name
        party.short_name = short_name
        party.color_hex = color_hex or None
        party.is_active = (is_active == "on")
        party.display_order = display_order
        party.founded_year = int(founded_year) if founded_year else None
        party.leader_name = leader_name or None
        party.house_of_representatives_seats = int(house_of_representatives_seats) if house_of_representatives_seats else None
        party.house_of_councillors_seats = int(house_of_councillors_seats) if house_of_councillors_seats else None
        party.ideology_summary = ideology_summary or None
        party.manifesto_summary = manifesto_summary or None
        party.manifesto_promises = _split_lines(manifesto_promises)
        party.main_policy_categories = _split_lines(main_policy_categories)
        party.official_url = official_url or None
        db.commit()
        return _redirect_with_msg("/admin/parties", "政党を更新しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/parties", f"エラーが発生しました: {e}", "error")


@router.post("/parties/{party_id}/delete")
def parties_delete(
    party_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 政党を取得して削除する
        party = db.query(Party).filter(Party.id == party_id).first()
        if not party:
            return _redirect_with_msg("/admin/parties", "政党が見つかりません", "error")
        db.delete(party)
        db.commit()
        return _redirect_with_msg("/admin/parties", "政党を削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/parties", f"エラーが発生しました: {e}", "error")


# ---------------------------------------------------------------------------
# カテゴリ管理
# ---------------------------------------------------------------------------

@router.get("/categories", response_class=HTMLResponse)
def categories_list(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. カテゴリ一覧を取得する
    categories = db.query(PolicyCategory).order_by(PolicyCategory.display_order).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/categories/list.html",
        context={"categories": categories, "admin": admin},
    )


@router.get("/categories/new", response_class=HTMLResponse)
def categories_new_page(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={"category": None, "admin": admin},
    )


@router.post("/categories/new")
def categories_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    display_order: int = Form(0),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. カテゴリを作成する
        category = PolicyCategory(
            name=name,
            slug=slug,
            description=description or None,
            display_order=display_order,
        )
        db.add(category)
        db.commit()
        return _redirect_with_msg("/admin/categories", "カテゴリを作成しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/categories", f"エラーが発生しました: {e}", "error")


@router.get("/categories/{cat_id}/edit", response_class=HTMLResponse)
def categories_edit_page(
    cat_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. カテゴリを取得する
    category = db.query(PolicyCategory).filter(PolicyCategory.id == cat_id).first()
    if not category:
        return _redirect_with_msg("/admin/categories", "カテゴリが見つかりません", "error")
    return templates.TemplateResponse(
        request=request,
        name="admin/categories/form.html",
        context={"category": category, "admin": admin},
    )


@router.post("/categories/{cat_id}/edit")
def categories_update(
    cat_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    display_order: int = Form(0),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. カテゴリを取得する
        category = db.query(PolicyCategory).filter(PolicyCategory.id == cat_id).first()
        if not category:
            return _redirect_with_msg("/admin/categories", "カテゴリが見つかりません", "error")
        # 3. カテゴリを更新する
        category.name = name
        category.slug = slug
        category.description = description or None
        category.display_order = display_order
        db.commit()
        return _redirect_with_msg("/admin/categories", "カテゴリを更新しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/categories", f"エラーが発生しました: {e}", "error")


@router.post("/categories/{cat_id}/delete")
def categories_delete(
    cat_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. カテゴリを取得して削除する
        category = db.query(PolicyCategory).filter(PolicyCategory.id == cat_id).first()
        if not category:
            return _redirect_with_msg("/admin/categories", "カテゴリが見つかりません", "error")
        db.delete(category)
        db.commit()
        return _redirect_with_msg("/admin/categories", "カテゴリを削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/categories", f"エラーが発生しました: {e}", "error")


# ---------------------------------------------------------------------------
# 統計データ管理
# ---------------------------------------------------------------------------

_STATS_PAGE_SIZE = 50


@router.get("/article-events", response_class=HTMLResponse)
def article_events_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 記事イベント一覧を取得する
    offset = (page - 1) * _STATS_PAGE_SIZE
    total = db.query(ArticleEvent).count()
    items = (
        db.query(ArticleEvent)
        .order_by(ArticleEvent.created_at.desc())
        .offset(offset)
        .limit(_STATS_PAGE_SIZE)
        .all()
    )
    total_pages = (total + _STATS_PAGE_SIZE - 1) // _STATS_PAGE_SIZE
    return templates.TemplateResponse(
        request=request,
        name="admin/stats/article_events.html",
        context={
            "items": items,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.post("/article-events/{event_id}/delete")
def article_events_delete(
    event_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. イベントを取得して削除する
        event = db.query(ArticleEvent).filter(ArticleEvent.id == event_id).first()
        if not event:
            return _redirect_with_msg("/admin/article-events", "イベントが見つかりません", "error")
        db.delete(event)
        db.commit()
        return _redirect_with_msg("/admin/article-events", "イベントを削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/article-events", f"エラーが発生しました: {e}", "error")


@router.get("/daily-article-stats", response_class=HTMLResponse)
def daily_article_stats_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 記事日次集計一覧を取得する
    offset = (page - 1) * _STATS_PAGE_SIZE
    total = db.query(DailyArticleStat).count()
    items = (
        db.query(DailyArticleStat)
        .order_by(DailyArticleStat.stat_date.desc())
        .offset(offset)
        .limit(_STATS_PAGE_SIZE)
        .all()
    )
    total_pages = (total + _STATS_PAGE_SIZE - 1) // _STATS_PAGE_SIZE
    return templates.TemplateResponse(
        request=request,
        name="admin/stats/daily_article_stats.html",
        context={
            "items": items,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.post("/daily-article-stats/{stat_id}/delete")
def daily_article_stats_delete(
    stat_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 集計レコードを取得して削除する
        stat = db.query(DailyArticleStat).filter(DailyArticleStat.id == stat_id).first()
        if not stat:
            return _redirect_with_msg("/admin/daily-article-stats", "レコードが見つかりません", "error")
        db.delete(stat)
        db.commit()
        return _redirect_with_msg("/admin/daily-article-stats", "レコードを削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/daily-article-stats", f"エラーが発生しました: {e}", "error")


@router.get("/daily-category-stats", response_class=HTMLResponse)
def daily_category_stats_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. カテゴリ日次集計一覧を取得する
    offset = (page - 1) * _STATS_PAGE_SIZE
    total = db.query(DailyCategoryStat).count()
    items = (
        db.query(DailyCategoryStat)
        .order_by(DailyCategoryStat.stat_date.desc())
        .offset(offset)
        .limit(_STATS_PAGE_SIZE)
        .all()
    )
    total_pages = (total + _STATS_PAGE_SIZE - 1) // _STATS_PAGE_SIZE
    return templates.TemplateResponse(
        request=request,
        name="admin/stats/daily_category_stats.html",
        context={
            "items": items,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.post("/daily-category-stats/{stat_id}/delete")
def daily_category_stats_delete(
    stat_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        # 2. 集計レコードを取得して削除する
        stat = db.query(DailyCategoryStat).filter(DailyCategoryStat.id == stat_id).first()
        if not stat:
            return _redirect_with_msg("/admin/daily-category-stats", "レコードが見つかりません", "error")
        db.delete(stat)
        db.commit()
        return _redirect_with_msg("/admin/daily-category-stats", "レコードを削除しました")
    except Exception as e:
        db.rollback()
        return _redirect_with_msg("/admin/daily-category-stats", f"エラーが発生しました: {e}", "error")


# ---------------------------------------------------------------------------
# 記事取り込み（Import）
# ---------------------------------------------------------------------------

_IMPORT_JOB_PAGE_SIZE = 30


@router.get("/imports", response_class=HTMLResponse)
def imports_index(request: Request, db: Session = Depends(get_db)):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 実行中ジョブを確認する
    active_job = get_active_job(db)
    return templates.TemplateResponse(
        request=request,
        name="admin/imports/index.html",
        context={
            "admin": admin,
            "active_job": active_job,
            "has_gemini": has_gemini_key(),
        },
    )


@router.post("/imports/run")
def imports_run(
    request: Request,
    db: Session = Depends(get_db),
    job_type: str = Form(...),
    single_url: str = Form(""),
    url_list_text: str = Form(""),
    url_source_name: str = Form("manual"),
    url_source_type: str = Form("party_official"),
    dry_run: str = Form(""),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. 実行中ジョブがある場合は拒否する
    if get_active_job(db):
        return _redirect_with_msg("/admin/imports", "別のジョブが実行中です。完了後に再試行してください", "error")
    # 3. Gemini 不要ジョブ以外はキー確認
    needs_gemini = job_type not in ("fetch_only",)
    if needs_gemini and not has_gemini_key():
        return _redirect_with_msg("/admin/imports", "GEMINI_API_KEY が設定されていません", "error")
    # 4. URL ソースを組み立てる
    url_sources = None
    if job_type == "url_list" and url_list_text.strip():
        lines = [ln.strip() for ln in url_list_text.splitlines() if ln.strip()]
        url_sources = [
            {
                "url": ln,
                "source_name": url_source_name or "manual",
                "source_type": url_source_type or "party_official",
            }
            for ln in lines
            if ln.startswith("http")
        ]
        if not url_sources:
            return _redirect_with_msg("/admin/imports", "有効な URL が見つかりません", "error")
    # 5. ジョブを作成して開始する
    params = JobParams(
        job_type=job_type,
        single_url=single_url.strip() or None,
        url_sources=url_sources,
        dry_run=(job_type == "dry_run") or (dry_run == "on"),
        fetch_only=(job_type == "fetch_only"),
    )
    job_id = create_and_start_job(params)
    return _redirect_with_msg(f"/admin/imports/jobs/{job_id}", "ジョブを開始しました")


@router.get("/imports/jobs", response_class=HTMLResponse)
def imports_jobs_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. ジョブ一覧を取得する
    offset = (page - 1) * _IMPORT_JOB_PAGE_SIZE
    total = db.query(ImportJob).count()
    jobs = (
        db.query(ImportJob)
        .order_by(ImportJob.created_at.desc())
        .offset(offset)
        .limit(_IMPORT_JOB_PAGE_SIZE)
        .all()
    )
    total_pages = (total + _IMPORT_JOB_PAGE_SIZE - 1) // _IMPORT_JOB_PAGE_SIZE
    return templates.TemplateResponse(
        request=request,
        name="admin/imports/jobs.html",
        context={
            "admin": admin,
            "jobs": jobs,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/imports/jobs/{job_id}", response_class=HTMLResponse)
def imports_job_detail(
    job_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. 認証ガード
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=302)
    # 2. ジョブと最新ログを取得する
    job = db.query(ImportJob).filter(ImportJob.id == job_id).first()
    if not job:
        return _redirect_with_msg("/admin/imports/jobs", "ジョブが見つかりません", "error")
    logs = (
        db.query(ImportJobLog)
        .filter(ImportJobLog.job_id == job_id)
        .order_by(ImportJobLog.created_at.asc())
        .all()
    )
    # running 中は 5 秒ごとに auto-refresh する
    auto_refresh = job.status in ("queued", "running")
    return templates.TemplateResponse(
        request=request,
        name="admin/imports/job_detail.html",
        context={
            "admin": admin,
            "job": job,
            "logs": logs,
            "auto_refresh": auto_refresh,
        },
    )
