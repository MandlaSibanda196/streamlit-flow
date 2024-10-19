import React from 'react';
import { Handle, Position } from 'reactflow';
import Markdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import 'katex/dist/katex.min.css';
import 'highlight.js/styles/github.css';



const MarkdownNode = ({ data }) => {
    return (
        <div className="markdown-node">
            <Markdown rehypePlugins={[rehypeHighlight, rehypeRaw, rehypeKatex]} remarkPlugins={[remarkGfm, remarkMath]}>
                {data.content}
            </Markdown>
            {data.columns && data.columns.length > 0 && (
                <div className="columns-list">
                    <h6>Columns:</h6>
                    <ul>
                        {data.columns.map((column, index) => (
                            <li key={index} className="column-item">
                                <span className="column-content">{column.column_name} ({column.type})</span>
                                <Handle
                                    type="source"
                                    position={Position.Right}
                                    id={`${data.id}-${column.column_name}-source`}
                                    className="handle handle-right"
                                />
                                <Handle
                                    type="target"
                                    position={Position.Left}
                                    id={`${data.id}-${column.column_name}-target`}
                                    className="handle handle-left"
                                />
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default MarkdownNode;
