import { useEffect, useState } from 'react';
import { createHighlighter, type Highlighter } from 'shiki';
import { useThemeStore } from '../../stores/useThemeStore';
import { Copy, Check } from 'lucide-react';
import { IconButton } from '../ui/IconButton';

interface SQLCodeBlockProps {
  code: string;
  showCopy?: boolean;
}

let highlighterInstance: Highlighter | null = null;

async function getHighlighter() {
  if (!highlighterInstance) {
    highlighterInstance = await createHighlighter({
      themes: ['github-dark-dimmed', 'github-light'],
      langs: ['sql'],
    });
  }
  return highlighterInstance;
}

export const SQLCodeBlock = ({ code, showCopy = true }: SQLCodeBlockProps) => {
  const { resolvedMode } = useThemeStore();
  const [highlightedCode, setHighlightedCode] = useState<string>('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function highlight() {
      try {
        const highlighter = await getHighlighter();
        const html = highlighter.codeToHtml(code, {
          lang: 'sql',
          theme: resolvedMode === 'dark' ? 'github-dark-dimmed' : 'github-light',
        });
        setHighlightedCode(html);
      } catch (error) {
        console.error('Failed to highlight code:', error);
        setHighlightedCode(`<pre><code>${code}</code></pre>`);
      }
    }

    highlight();
  }, [code, resolvedMode]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  return (
    <div className="relative group">
      {showCopy && (
        <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
          <IconButton
            onClick={handleCopy}
            size="sm"
            aria-label={copied ? 'Copied!' : 'Copy code'}
            title={copied ? 'Copied!' : 'Copy code'}
            className="bg-light-elevated dark:bg-dark-elevated"
          >
            {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
          </IconButton>
        </div>
      )}
      <div
        className="shiki-container overflow-x-auto text-sm"
        dangerouslySetInnerHTML={{ __html: highlightedCode }}
      />
    </div>
  );
};
