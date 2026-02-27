"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { channelsApi } from "@/lib/api"
import Link from "next/link"
import { ArrowLeft, Plus, Trash2 } from "lucide-react"

export default function ChannelsPage() {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({ platform_name: "", api_identifier: "" })

  const { data: channels, isLoading } = useQuery({
    queryKey: ["channels"],
    queryFn: channelsApi.list,
  })

  const createMutation = useMutation({
    mutationFn: channelsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["channels"] })
      setIsCreating(false)
      setFormData({ platform_name: "", api_identifier: "" })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: channelsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["channels"] })
    },
  })

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/admin" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Admin
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Channels</h1>
              <p className="text-muted-foreground">Manage advertising platforms</p>
            </div>
            <button onClick={() => setIsCreating(!isCreating)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition">
              <Plus className="w-4 h-4" />
              Create Channel
            </button>
          </div>
        </div>

        {isCreating && (
          <div className="mb-6 p-6 rounded-lg border border-border bg-card">
            <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(formData) }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Platform Name</label>
                <input type="text" value={formData.platform_name} onChange={(e) => setFormData({ ...formData, platform_name: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Meta" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">API Identifier</label>
                <input type="text" value={formData.api_identifier} onChange={(e) => setFormData({ ...formData, api_identifier: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="meta_marketing_api" required />
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
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Platform</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">API</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr><td colSpan={3} className="px-6 py-4 text-center text-muted-foreground">Loading...</td></tr>
              ) : channels?.length === 0 ? (
                <tr><td colSpan={3} className="px-6 py-4 text-center text-muted-foreground">No channels found.</td></tr>
              ) : (
                channels?.map((channel: any) => (
                  <tr key={channel.id} className="hover:bg-secondary/50">
                    <td className="px-6 py-4 font-medium">{channel.platform_name}</td>
                    <td className="px-6 py-4 text-muted-foreground">{channel.api_identifier}</td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => { if (confirm(`Delete channel ${channel.platform_name}?`)) { deleteMutation.mutate(channel.id) }}} className="text-destructive hover:text-destructive/80 transition">
                        <Trash2 className="w-4 h-4" />
                      </button>
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
