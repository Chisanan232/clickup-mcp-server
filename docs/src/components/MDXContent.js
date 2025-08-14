import React from 'react';

/**
 * This component serves as a wrapper for MDX content that might confuse the MDX parser.
 * It helps prevent the "Unexpected FunctionDeclaration" errors by ensuring content is
 * treated as plain text/markdown rather than executable code.
 */
export default function MDXContent({children}) {
  return <div className="mdx-content-wrapper">{children}</div>;
}
