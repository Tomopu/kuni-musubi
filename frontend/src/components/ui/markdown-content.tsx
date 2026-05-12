import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";

type Props = {
  children: string;
  className?: string;
};

// LLM 生成テキストを Markdown として安全にレンダリングする。
// dangerouslySetInnerHTML は使わず、rehype-sanitize で生成後の HTML AST も許可リスト化する。
export function MarkdownContent({ children, className }: Props) {
  return (
    <div className={`markdown-content${className ? ` ${className}` : ""}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        disallowedElements={["script", "iframe", "object", "embed", "form"]}
        unwrapDisallowed
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
