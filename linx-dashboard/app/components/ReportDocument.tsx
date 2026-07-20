import type { ReactNode } from "react";

type ReportDocumentProps = {
  content: string;
};

const inlinePattern = /(\*\*.+?\*\*|__.+?__|`[^`]+`|\[[^\]]+\]\(https?:\/\/[^)\s]+\)|\*[^*\n]+\*)/g;

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  return text.split(inlinePattern).filter(Boolean).map((part, index) => {
    const key = `${keyPrefix}-${index}`;
    if ((part.startsWith("**") && part.endsWith("**")) || (part.startsWith("__") && part.endsWith("__"))) {
      return <strong key={key}>{renderInline(part.slice(2, -2), `${key}-strong`)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) return <code key={key}>{part.slice(1, -1)}</code>;
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
    if (link) return <a key={key} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a>;
    if (part.startsWith("*") && part.endsWith("*")) return <em key={key}>{part.slice(1, -1)}</em>;
    return part;
  });
}

function isTableDivider(line: string) {
  const cells = line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
  return cells.length > 1 && cells.every((cell) => /^:?-{3,}:?$/.test(cell));
}

function tableCells(line: string) {
  return line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
}

function startsBlock(line: string, nextLine?: string) {
  const value = line.trim();
  return !value || /^#{1,3}\s+/.test(value) || /^(?:-{3,}|_{3,}|\*{3,})$/.test(value) || /^[-*•]\s+/.test(value) || /^\d+[.)]\s+/.test(value) || /^>\s?/.test(value) || (value.includes("|") && Boolean(nextLine && isTableDivider(nextLine)));
}

export default function ReportDocument({ content }: ReportDocumentProps) {
  const lines = content.replace(/\r\n?/g, "\n").split("\n");
  const blocks: ReactNode[] = [];

  for (let index = 0; index < lines.length;) {
    const line = lines[index].trim();
    if (!line) { index += 1; continue; }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      if (level === 1) blocks.push(<h1 key={`heading-${index}`}>{renderInline(heading[2], `heading-${index}`)}</h1>);
      else if (level === 2) blocks.push(<h2 key={`heading-${index}`}>{renderInline(heading[2], `heading-${index}`)}</h2>);
      else blocks.push(<h3 key={`heading-${index}`}>{renderInline(heading[2], `heading-${index}`)}</h3>);
      index += 1;
      continue;
    }

    if (/^(?:-{3,}|_{3,}|\*{3,})$/.test(line)) {
      blocks.push(<hr key={`rule-${index}`} />);
      index += 1;
      continue;
    }

    if (line.includes("|") && lines[index + 1] && isTableDivider(lines[index + 1])) {
      const header = tableCells(line);
      const rows: string[][] = [];
      index += 2;
      while (index < lines.length && lines[index].trim().includes("|")) {
        rows.push(tableCells(lines[index]));
        index += 1;
      }
      blocks.push(
        <div className="report-table-wrap" key={`table-${index}`}>
          <table><thead><tr>{header.map((cell, cellIndex) => <th key={cellIndex}>{renderInline(cell, `th-${index}-${cellIndex}`)}</th>)}</tr></thead>
            <tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{renderInline(cell, `td-${index}-${rowIndex}-${cellIndex}`)}</td>)}</tr>)}</tbody>
          </table>
        </div>,
      );
      continue;
    }

    const unordered = line.match(/^[-*•]\s+(.+)$/);
    if (unordered) {
      const items: string[] = [];
      while (index < lines.length) {
        const item = lines[index].trim().match(/^[-*•]\s+(.+)$/);
        if (!item) break;
        items.push(item[1]);
        index += 1;
      }
      blocks.push(<ul key={`list-${index}`}>{items.map((item, itemIndex) => <li key={itemIndex}>{renderInline(item, `li-${index}-${itemIndex}`)}</li>)}</ul>);
      continue;
    }

    const ordered = line.match(/^\d+[.)]\s+(.+)$/);
    if (ordered) {
      const items: string[] = [];
      while (index < lines.length) {
        const item = lines[index].trim().match(/^\d+[.)]\s+(.+)$/);
        if (!item) break;
        items.push(item[1]);
        index += 1;
      }
      blocks.push(<ol key={`list-${index}`}>{items.map((item, itemIndex) => <li key={itemIndex}>{renderInline(item, `oli-${index}-${itemIndex}`)}</li>)}</ol>);
      continue;
    }

    if (line.startsWith(">")) {
      const quote: string[] = [];
      while (index < lines.length && lines[index].trim().startsWith(">")) {
        quote.push(lines[index].trim().replace(/^>\s?/, ""));
        index += 1;
      }
      blocks.push(<blockquote key={`quote-${index}`}>{renderInline(quote.join(" "), `quote-${index}`)}</blockquote>);
      continue;
    }

    const paragraph = [line];
    index += 1;
    while (index < lines.length && !startsBlock(lines[index], lines[index + 1])) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    blocks.push(<p key={`paragraph-${index}`}>{renderInline(paragraph.join(" "), `paragraph-${index}`)}</p>);
  }

  return <article className="report-document">{blocks}</article>;
}
