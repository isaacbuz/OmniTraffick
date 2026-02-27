"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { brandsApi } from "@/lib/api"
import Link from "next/link"
import { ArrowLeft, Plus, Trash2 } from "lucide-react"

export default function BrandsPage() {
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({ name: "", internal_code: "" })

  const { data: brands, isLoading } = useQuery({
    queryKey: ["brands"],
    queryFn: brandsApi.list,
  })

  const createMutation = useMutation({
    mutationFn: brandsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brands"] })
      setIsCreating(false)
      setFormData({ name: "", internal_code: "" })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: brandsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brands"] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

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
              <h1 className="text-4xl font-bold mb-2">Brands</h1>
              <p className="text-muted-foreground">Manage advertiser brands</p>
            </div>
            <button onClick={() => setIsCreating(!isCreating)} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition">
              <Plus className="w-4 h-4" />
              Create Brand
            </button>
          </div>
        </div>

        {isCreating && (
          <div className="mb-6 p-6 rounded-lg border border-border bg-card">
            <h3 className="text-lg font-semibold mb-4">Create New Brand</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Brand Name</label>
                <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="Disney+" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Internal Code</label>
                <input type="text" value={formData.internal_code} onChange={(e) => setFormData({ ...formData, internal_code: e.target.value.toUpperCase() })} className="w-full px-3 py-2 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary" placeholder="DIS" maxLength={5} required />
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={createMutation.isPending} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50">
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
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Brand</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase">Code</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr><td colSpan={3} className="px-6 py-4 text-center text-muted-foreground">Loading...</td></tr>
              ) : brands?.length === 0 ? (
                <tr><td colSpan={3} className="px-6 py-4 text-center text-muted-foreground">No brands found.</td></tr>
              ) : (
                brands?.map((brand: any) => (
                  <tr key={brand.id} className="hover:bg-secondary/50">
                    <td className="px-6 py-4 font-medium">{brand.name}</td>
                    <td className="px-6 py-4"><code className="px-2 py-1 rounded bg-primary/20 text-primary">{brand.internal_code}</code></td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => { if (confirm(`Delete brand ${brand.name}?`)) { deleteMutation.mutate(brand.id) }}} className="text-destructive hover:text-destructive/80 transition">
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
