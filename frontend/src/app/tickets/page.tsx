"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ticketsApi, campaignsApi, channelsApi, deployApi } from "@/lib/api"
import Link from "next/link"
import { ArrowLeft, Plus, Play, CheckCircle2, XCircle, AlertCircle, Clock } from "lucide-react"

export default function TicketsPage() {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState("")
  const [selectedChannel, setSelectedChannel] = useState("")
  const [payloadConfig, setPayloadConfig] = useState({
    ad_account_id: "",
    objective: "OUTCOME_TRAFFIC",
    targeting: {
      geo_locations: {
        countries: ["US"]
      }
    }
  })

  const { data: tickets } = useQuery({
    queryKey: ["tickets"],
    queryFn: ticketsApi.list,
  })

  const { data: campaigns } = useQuery({
    queryKey: ["campaigns"],
    queryFn: campaignsApi.list,
  })

  const { data: channels } = useQuery({
    queryKey: ["channels"],
    queryFn: channelsApi.list,
  })

  const createMutation = useMutation({
    mutationFn: ticketsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
      setIsCreating(false)
      setSelectedCampaign("")
      setSelectedChannel("")
    },
  })

  const deployMutation = useMutation({
    mutationFn: (ticketId: string) => deployApi.deploy(ticketId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      campaign_id: selectedCampaign,
      channel_id: selectedChannel,
      request_type: "CREATE_CAMPAIGN",
      payload_config: payloadConfig,
    })
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, any> = {
      DRAFT: { icon: Clock, className: "bg-muted text-muted-foreground" },
      QA_TESTING: { icon: AlertCircle, className: "bg-yellow-500/20 text-yellow-400" },
      QA_FAILED: { icon: XCircle, className: "bg-destructive/20 text-destructive" },
      READY_FOR_API: { icon: CheckCircle2, className: "bg-green-500/20 text-green-400" },
      TRAFFICKED_SUCCESS: { icon: CheckCircle2, className: "bg-green-500/30 text-green-300" },
      FAILED: { icon: XCircle, className: "bg-destructive/30 text-destructive" },
    }
    const config = badges[status] || badges.DRAFT
    const Icon = config.icon
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${config.className}`}>
        <Icon className="w-3 h-3" />
        {status.replace(/_/g, " ")}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Trafficking Tickets</h1>
              <p className="text-muted-foreground">Create and manage API deployment requests</p>
            </div>
            <button onClick={() => setIsCreating(!isCreating)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition">
              <Plus className="w-4 h-4" />
              Create Ticket
            </button>
          </div>
        </div>

        {isCreating && (
          <div className="mb-6 p-6 rounded-lg border border-border bg-card">
            <h3 className="text-lg font-semibold mb-4">Create Trafficking Ticket</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Campaign</label>
                  <select value={selectedCampaign} onChange={(e) => setSelectedCampaign(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" required>
                    <option value="">Select campaign</option>
                    {campaigns?.map((c: any) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Channel</label>
                  <select value={selectedChannel} onChange={(e) => setSelectedChannel(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" required>
                    <option value="">Select channel</option>
                    {channels?.map((ch: any) => (
                      <option key={ch.id} value={ch.id}>{ch.platform_name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Ad Account ID</label>
                <input type="text" value={payloadConfig.ad_account_id} onChange={(e) => setPayloadConfig({ ...payloadConfig, ad_account_id: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="123456789" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Objective</label>
                <select value={payloadConfig.objective} onChange={(e) => setPayloadConfig({ ...payloadConfig, objective: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="OUTCOME_TRAFFIC">Traffic</option>
                  <option value="OUTCOME_LEADS">Leads</option>
                  <option value="OUTCOME_SALES">Sales</option>
                  <option value="OUTCOME_AWARENESS">Awareness</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50">
                  {createMutation.isPending ? "Creating..." : "Create Ticket"}
                </button>
                <button type="button" onClick={() => setIsCreating(false)} className="px-4 py-2 rounded-lg bg-secondary text-foreground hover:bg-secondary/80 transition">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full">
            <thead className="bg-secondary">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Campaign</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Channel</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {tickets?.length === 0 ? (
                <tr><td colSpan={4} className="px-6 py-4 text-center text-muted-foreground">No tickets found.</td></tr>
              ) : (
                tickets?.map((ticket: any) => (
                  <tr key={ticket.id} className="hover:bg-secondary/50">
                    <td className="px-6 py-4 font-medium">{ticket.campaign?.name || "N/A"}</td>
                    <td className="px-6 py-4">{ticket.channel?.platform_name || "N/A"}</td>
                    <td className="px-6 py-4">{getStatusBadge(ticket.status)}</td>
                    <td className="px-6 py-4 text-right">
                      {ticket.status === "READY_FOR_API" && (
                        <button onClick={() => deployMutation.mutate(ticket.id)} disabled={deployMutation.isPending} className="inline-flex items-center gap-1 px-3 py-1 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50 text-sm">
                          <Play className="w-3 h-3" />
                          Deploy
                        </button>
                      )}
                      {ticket.status === "TRAFFICKED_SUCCESS" && ticket.external_platform_id && (
                        <span className="text-xs text-muted-foreground">ID: {ticket.external_platform_id}</span>
                      )}
                      {ticket.status === "QA_FAILED" && ticket.qa_failure_reason && (
                        <span className="text-xs text-destructive">{ticket.qa_failure_reason}</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
