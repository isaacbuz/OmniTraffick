"use client"

import Link from "next/link"
import { Database, Tag, Radio, ArrowLeft } from "lucide-react"

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Data Governance Hub - Manage metadata that powers the taxonomy engine
          </p>
        </div>

        {/* Governance Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <Link href="/admin/markets">
            <div className="p-6 rounded-lg border border-border bg-card hover:bg-card/80 transition cursor-pointer">
              <Database className="w-10 h-10 text-primary mb-4" />
              <h2 className="text-xl font-semibold mb-2">Markets</h2>
              <p className="text-muted-foreground text-sm mb-4">
                Geographic targeting regions (US, UK, EMEA)
              </p>
              <div className="flex items-center text-sm text-primary">
                Manage Markets
                <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
              </div>
            </div>
          </Link>

          <Link href="/admin/brands">
            <div className="p-6 rounded-lg border border-border bg-card hover:bg-card/80 transition cursor-pointer">
              <Tag className="w-10 h-10 text-primary mb-4" />
              <h2 className="text-xl font-semibold mb-2">Brands</h2>
              <p className="text-muted-foreground text-sm mb-4">
                Advertiser brands with internal codes (DIS, HULU)
              </p>
              <div className="flex items-center text-sm text-primary">
                Manage Brands
                <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
              </div>
            </div>
          </Link>

          <Link href="/admin/channels">
            <div className="p-6 rounded-lg border border-border bg-card hover:bg-card/80 transition cursor-pointer">
              <Radio className="w-10 h-10 text-primary mb-4" />
              <h2 className="text-xl font-semibold mb-2">Channels</h2>
              <p className="text-muted-foreground text-sm mb-4">
                Ad platforms (Meta, TikTok, Google Ads)
              </p>
              <div className="flex items-center text-sm text-primary">
                Manage Channels
                <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
              </div>
            </div>
          </Link>
        </div>

        {/* Info Box */}
        <div className="mt-8 p-4 rounded-lg bg-primary/10 border border-primary/20">
          <p className="text-sm">
            <strong>Taxonomy Engine:</strong> Changes to Markets, Brands, or Channels immediately affect
            future campaign name generation. All campaigns use the format:{" "}
            <code className="px-2 py-1 rounded bg-background/50">
              [BrandCode]_[MarketCode]_[Channel]_[Year]_[CampaignName]
            </code>
          </p>
        </div>
      </div>
    </div>
  )
}
