"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { Brain, Sparkles, X } from "lucide-react"

interface RAGSuggestion {
  text: string
  score: number
  source: string
}

interface RAGCopilotProps {
  ticketContext: {
    brand?: string
    campaign_name?: string
    channel?: string
    market?: string
  }
}

export function RAGCopilot({ ticketContext }: RAGCopilotProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [suggestion, setSuggestion] = useState<string | null>(null)

  const getSuggestionMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch("/api/v1/rag/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ticketContext),
      })
      return response.json()
    },
    onSuccess: (data) => {
      setSuggestion(data.suggestion)
      setIsOpen(true)
    },
  })

  if (!ticketContext.brand || !ticketContext.channel) {
    return null
  }

  return (
    <div className="relative">
      <button
        onClick={() => getSuggestionMutation.mutate()}
        disabled={getSuggestionMutation.isPending}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/30 text-purple-300 hover:bg-purple-500/30 transition disabled:opacity-50"
      >
        <Brain className="w-4 h-4" />
        {getSuggestionMutation.isPending ? "Analyzing..." : "AI Copilot Suggestion"}
        <Sparkles className="w-3 h-3" />
      </button>

      {isOpen && suggestion && (
        <div className="absolute top-full mt-2 left-0 right-0 z-50 p-4 rounded-lg border border-purple-500/30 bg-purple-500/10 backdrop-blur">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2 text-purple-300">
              <Brain className="w-4 h-4" />
              <span className="text-sm font-medium">AI Recommendation</span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="text-sm text-foreground leading-relaxed">{suggestion}</p>
          <div className="mt-3 text-xs text-muted-foreground">
            Based on brand guidelines and historical performance data
          </div>
        </div>
      )}
    </div>
  )
}
