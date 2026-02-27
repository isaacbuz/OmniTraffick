"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { campaignsApi, brandsApi, marketsApi, ticketsApi, deployApi } from "@/lib/api"
import Link from "next/link"
import { ArrowLeft, Plus, Play, CheckCircle2, XCircle, Clock } from "lucide-react"

export default function CampaignsPage() {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    campaign_name: "",
    brand_id: "",
    market_id: "",
    budget: 10000,
  })

  const { data: campaigns } = useQuery({
    queryKey: ["campaigns"],
    queryFn: campaignsApi.list,
  })

  const { data: brands } = useQuery({
    queryKey: ["brands"],
    queryFn: brandsApi.list,
  })

  const { data: markets } = useQuery({
    queryKey: ["markets"],
    queryFn: marketsApi.list,
  })

  const createMutation = useMutation({
    mutationFn: campaignsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] })
      setIsCreating(false)
      setFormData({ campaign_name: "", brand_id: "", market_id: "", budget: 10000 })
    },
  })

  const getStatusBadge = (status: string) => {
    const badges: Record<string, any> = {
      DRAFT: { icon: Clock, className: "bg-muted text-muted-foreground" },
      ACTIVE: { icon: CheckCircle2, className: "bg-green-500/20 text-green-400" },
      PAUSED: { icon: Clock, className: "bg-yellow-500/20 text-yellow-400" },
      COMPLETED: { icon: CheckCircle2, className: "bg-blue-500/20 text-blue-400" },
    }
    const config = badges[status] || badges.DRAFT
    const Icon = config.icon
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${config.className}`}>
        <Icon className="w-3 h-3" />
        {status}
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
              <h1 className="text-4xl font-bold mb-2">Campaigns</h1>
              <p className="text-muted-foreground">Manage advertising campaigns</p>
            </div>
            <button onClick={() => setIsCreating(!isCreating)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition">
              <Plus className="w-4 h-4" />
              Create Campaign
            </button>
          </div>
        </div>

        {isCreating && (
          <div className="mb-6 p-6 rounded-lg border border-border bg-card">
            <h3 className="text-lg font-semibold mb-4">Create New Campaign</h3>
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(formData) }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Campaign Name</label>
                <input type="text" value={formData.campaign_name} onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="MoanaLaunch" required />
                <p className="text-xs text-muted-foreground mt-1">Final name will be auto-generated with taxonomy</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Brand</label>
                  <select value={formData.brand_id} onChange={(e) => setFormData({ ...formData, brand_id: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" required>
                    <option value="">Select brand</option>
                    {brands?.map((b: any) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.internal_code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Market</label>
                  <select value={formData.market_id} onChange={(e) => setFormData({ ...formData, market_id: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" required>
                    <option value="">Select market</option>
                    {markets?.map((m: any) => (
                      <option key={m.id} value={m.id}>{m.country} ({m.code})</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Budget ($)</label>
                <input type="number" value={formData.budget} onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" min="0" step="100" required />
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition">
                  {createMutation.isPending ? "Creating..." : "Create"}
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
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Budget</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {campaigns?.length === 0 ? (
                <tr><td colSpan={3} className="px-6 py-4 text-center text-muted-foreground">No campaigns found.</td></tr>
              ) : (
                campaigns?.map((campaign: any) => (
                  <tr key={campaign.id} className="hover:bg-secondary/50">
                    <td className="px-6 py-4">
                      <div className="font-medium">{campaign.name}</div>
                      <div className="text-sm text-muted-foreground">{campaign.campaign_name}</div>
                    </td>
                    <td className="px-6 py-4">${campaign.budget?.toLocaleString()}</td>
                    <td className="px-6 py-4">{getStatusBadge(campaign.status)}</td>
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
