import React from 'react';
import { Box } from '@mui/material';
import Editor from '@monaco-editor/react';

export type EditorType = 'layout' | 'partial' | 'template';

interface EditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  type?: EditorType;
  height?: string;
}

const EDITOR_CONFIGS = {
  layout: {
    language: 'html',
    fontSize: 14,
    minimap: { enabled: false },
    wordWrap: 'on' as const,
    automaticLayout: true,
    suggestOnTriggerCharacters: true,
    quickSuggestions: true,
    snippetSuggestions: 'inline' as const,
    suggest: {
      showWords: true,
      showSnippets: true,
      showClasses: true,
      showFunctions: true,
      showVariables: true,
      showProperties: true,
      showColors: true,
      showFiles: true,
      showReferences: true,
      showFolders: true,
      showTypeParameters: true,
      showEnums: true,
      showEnumMembers: true,
      showKeywords: true
    }
  },
  partial: {
    language: 'html',
    fontSize: 14,
    minimap: { enabled: false },
    wordWrap: 'on' as const,
    automaticLayout: true,
    suggestOnTriggerCharacters: true,
    quickSuggestions: true,
    snippetSuggestions: 'inline' as const,
    suggest: {
      showWords: true,
      showSnippets: true,
      showClasses: true,
      showFunctions: true,
      showVariables: true,
      showProperties: true,
      showColors: true,
      showFiles: true,
      showReferences: true,
      showFolders: true,
      showTypeParameters: true,
      showEnums: true,
      showEnumMembers: true,
      showKeywords: true
    }
  },
  template: {
    language: 'html',
    fontSize: 14,
    minimap: { enabled: false },
    wordWrap: 'on' as const,
    automaticLayout: true,
    suggestOnTriggerCharacters: true,
    quickSuggestions: true,
    snippetSuggestions: 'inline' as const,
    suggest: {
      showWords: true,
      showSnippets: true,
      showClasses: true,
      showFunctions: true,
      showVariables: true,
      showProperties: true,
      showColors: true,
      showFiles: true,
      showReferences: true,
      showFolders: true,
      showTypeParameters: true,
      showEnums: true,
      showEnumMembers: true,
      showKeywords: true
    }
  }
};

export function HtmlEditor({ 
  value, 
  onChange, 
  readOnly = false, 
  type = 'layout',
  height = '100%'
}: EditorProps) {
  const config = EDITOR_CONFIGS[type];

  return (
    <Box sx={{ height, overflow: 'hidden' }}>
      <Editor
        height={height}
        defaultLanguage={config.language}
        value={value}
        onChange={(value) => onChange(value || '')}
        options={{
          ...config,
          readOnly,
          suggestOnTriggerCharacters: !readOnly,
          quickSuggestions: !readOnly,
          snippetSuggestions: readOnly ? 'none' : 'inline',
          suggest: {
            ...config.suggest,
            showWords: !readOnly,
            showSnippets: !readOnly,
            showClasses: !readOnly,
            showFunctions: !readOnly,
            showVariables: !readOnly,
            showProperties: !readOnly,
            showColors: !readOnly,
            showFiles: !readOnly,
            showReferences: !readOnly,
            showFolders: !readOnly,
            showTypeParameters: !readOnly,
            showEnums: !readOnly,
            showEnumMembers: !readOnly,
            showKeywords: !readOnly
          }
        }}
      />
    </Box>
  );
} 