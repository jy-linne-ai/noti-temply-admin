import React, { useEffect, useState, useRef } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';

interface PreviewProps {
  content: string;
  title?: string;
  type?: 'layout' | 'template' | 'partial';
  onRender?: () => Promise<string>;
  componentName?: string;
}

const PREVIEW_STYLES = {
  layout: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
  template: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
  partial: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
};

export function Preview({ content, title, type = 'template', onRender, componentName }: PreviewProps) {
  const styles = PREVIEW_STYLES[type];
  const [renderedContent, setRenderedContent] = useState<string>(content);
  const [isLoading, setIsLoading] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const renderContent = async () => {
      if (onRender) {
        try {
          setIsLoading(true);
          const rendered = await onRender();
          const formattedContent = componentName === 'TEXT_EMAIL' 
            ? rendered.replace(/\n/g, '<br>')
            : rendered;
          setRenderedContent(formattedContent);
        } catch (error) {
          console.error('Error rendering content:', error);
          setRenderedContent(content);
        } finally {
          setIsLoading(false);
        }
      }
    };

    renderContent();
  }, [content, onRender, componentName]);

  // iframe에 콘텐츠 주입
  useEffect(() => {
    if (iframeRef.current) {
      const iframe = iframeRef.current;
      const doc = iframe.contentDocument || iframe.contentWindow?.document;
      if (doc) {
        doc.open();
        doc.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <style>
                html, body {
                  margin: 0;
                  padding: 0;
                  min-height: 100%;
                  width: 100%;
                }
                body {
                  font-family: Arial, sans-serif;
                  font-size: 14px;
                  line-height: 1.5;
                  color: #333;
                }
                .container {
                  padding: 20px;
                  box-sizing: border-box;
                }
                pre {
                  white-space: pre-wrap;
                  word-break: break-word;
                  font-family: monospace;
                  font-size: 0.875rem;
                  margin: 0;
                }
              </style>
              <script>
                function updateHeight() {
                  const height = document.documentElement.scrollHeight;
                  window.parent.postMessage({ type: 'resize', height }, '*');
                }
                
                // 초기 로드 시 높이 업데이트
                window.addEventListener('load', updateHeight);
                
                // DOM 변경 감지
                const observer = new MutationObserver(updateHeight);
                observer.observe(document.body, {
                  childList: true,
                  subtree: true,
                  characterData: true
                });
                
                // 이미지 로드 완료 시 높이 업데이트
                document.addEventListener('load', function(e) {
                  if (e.target.tagName === 'IMG') {
                    updateHeight();
                  }
                }, true);
              </script>
            </head>
            <body>
              <div class="container">
                ${renderedContent}
              </div>
            </body>
          </html>
        `);
        doc.close();
      }
    }
  }, [renderedContent]);

  // iframe 메시지 이벤트 처리
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'resize' && iframeRef.current) {
        iframeRef.current.style.height = `${event.data.height}px`;
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <Box
      sx={{
        flex: 1,
        minHeight: 0,
        overflow: 'hidden',
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {isLoading && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'rgba(255, 255, 255, 0.7)',
            zIndex: 1,
          }}
        >
          <CircularProgress />
        </Box>
      )}
      <iframe
        ref={iframeRef}
        style={{
          width: '100%',
          border: 'none',
          overflow: 'hidden',
          flex: 1,
        }}
        title="Preview"
      />
    </Box>
  );
} 