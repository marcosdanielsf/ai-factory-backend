'use client'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
}

export function CodeEditor({ value, onChange }: CodeEditorProps) {
  const lines = value.split('\n')
  const lineNumbers = Array.from({ length: Math.max(30, lines.length) }, (_, i) => i + 1)

  return (
    <div className="flex-1 flex flex-col relative bg-[#1e1e1e]">
      {/* Line Numbers */}
      <div className="absolute left-0 top-0 bottom-0 w-10 bg-[#1e1e1e] border-r border-[#2d2d2d] flex flex-col items-end pt-4 pr-2 text-text-muted/50 font-mono text-sm select-none z-10">
        {lineNumbers.map((num) => (
          <div key={num} className="leading-6">{num}</div>
        ))}
      </div>

      {/* Editor */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck="false"
        className="w-full h-full bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm p-4 pl-12 resize-none focus:outline-none leading-6"
        style={{ tabSize: 2 }}
        placeholder="Digite o system_prompt do agente aqui..."
      />
    </div>
  )
}
