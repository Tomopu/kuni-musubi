export default async function ArticleDetailPage({
  params,
}: {
  params: Promise<{ articleId: string }>;
}) {
  const { articleId } = await params;
  return <div data-article-id={articleId} />;
}
