"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ticketsApi, deployApi } from "@/lib/api"
import Link from "next/link"
import { ArrowLeft, Play } from "lucide-react"

const COLUMNS = [
  { id: "DRAFT", label: "Draft", color: "bg-muted" },
  { id: "QA_TESTING", label: "QA Testing", color: "bg-yellow-500/20" },
  { id: "READY_FOR_API", label: "Ready for API", color: "bg-green-500/20" },
  { id: "TRAFFICKED_SUCCESS", label: "Deployed", color: "bg-blue-500/20" },
]

export default function KanbanPage() {
  const queryClient = useQueryClient()
  const [draggingId, setDraggingId] = useState<string | null>(null)

  const { data: tickets } = useQuery({
    queryKey: ["tickets"],
    queryFn: ticketsApi.list,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      ticketsApi.update(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    },
  })

  const deployMutation = useMutation({
    mutationFn: (ticketId: string) => deployApi.deploy(ticketId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    },
  })

  const handleDragStart = (e: React.DragEvent, ticketId: string) => {
    setDraggingId(ticketId)
    e.dataTransfer.effectAllowed = "move"
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = "move"
  }

  const handleDrop = (e: React.DragEvent, targetStatus: string) => {
    e.preventDefault()
    if (!draggingId) return

    const ticket = tickets?.find((t: any) => t.id === draggingId)
    if (!ticket) return

    // Allow certain transitions
    const allowedTransitions: Record<string, string[]> = {
      DRAFT: ["QA_TESTING"],
      QA_TESTING: ["DRAFT", "READY_FOR_API"],
      READY_FOR_API: ["QA_TESTING"],
    }

    if (allowedTransitions[ticket.status]?.includes(targetStatus)) {
      updateMutation.mutate({ id: draggingId, status: targetStatus })
    }

    setDraggingId(null)
  }

  const groupedTickets = COLUMNS.reduce((acc, col) => {
    acc[col.id] = tickets?.filter((t: any) => t.status === col.id) || []
    return acc
  }, {} as Record<string, any[]>)

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div>
            <h1 className="text-4xl font-bold mb-2">Trafficking Kanban</h1>
            <p className="text-muted-foreground">Drag tickets between stages</p>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          {COLUMNS.map((column) => (
            <div
              key={column.id}
              className="rounded-lg border border-border bg-card/50 p-4"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.id)}
            >
              <div className="mb-4">
                <h3 className="font-semibold mb-1">{column.label}</h3>
                <div className="text-sm text-muted-foreground">
                  {groupedTickets[column.id]?.length || 0} tickets
                </div>
              </div>

              <div className="space-y-2">
                {groupedTickets[column.id]?.map((ticket: any) => (
                  <div
                    key={ticket.id}
                    draggable={column.id !== "TRAFFICKED_SUCCESS"}
                    onDragStart={(e) => handleDragStart(e, ticket.id)}
                    className={`p-3 rounded-lg border border-border ${column.color} cursor-move hover:opacity-80 transition ${
                      draggingId === ticket.id ? "opacity-50" : ""
                    }`}
                  >
                    <div className="font-medium text-sm mb-1">
                      {ticket.campaign?.name || "Unknown Campaign"}
                    </div>
                    <div className="text-xs text-muted-foreground mb-2">
                      {ticket.channel?.platform_name || "Unknown Channel"}
                    </div>
                    {column.id === "READY_FOR_API" && (
                      <button
                        onClick={() => deployMutation.mutate(ticket.id)}
                        disabled={deployMutation.isPending}
                        className="w-full flex items-center justify-center gap-1 px-2 py-1 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition text-xs disabled:opacity-50"
                      >
                        <Play className="w-3 h-3" />
                        Deploy
                      </button>
                    )}
                    {column.id === "TRAFFICKED_SUCCESS" && ticket.external_platform_id && (
                      <div className="text-xs text-green-400">
                        ID: {ticket.external_platform_id.slice(0, 12)}...
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 rounded-lg bg-primary/10 border border-primary/20">
          <p className="text-sm">
            <strong>Workflow:</strong> Drag tickets from DRAFT → QA TESTING to run validation. 
            If QA passes, ticket moves to READY FOR API. Click Deploy to queue async deployment. 
            Successful deployments move to DEPLOYED column.
          </p>
        </div>
      </div>
    </div>
  )
}
