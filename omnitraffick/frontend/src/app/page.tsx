import Link from "next/link"
import { ArrowRight, Shield, Zap, Brain } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-primary via-yellow-500 to-primary bg-clip-text text-transparent">
            OmniTraffick
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Enterprise AdOps Orchestration Platform
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur">
            <Shield className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">QA Rules Engine</h3>
            <p className="text-muted-foreground">
              Automated pre-flight validation blocks non-compliant payloads before they reach the API.
            </p>
          </div>
          
          <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur">
            <Zap className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Async Deployment</h3>
            <p className="text-muted-foreground">
              Celery-powered task queue with exponential backoff and rate limit handling.
            </p>
          </div>
          
          <div className="p-6 rounded-lg border border-border bg-card/50 backdrop-blur">
            <Brain className="w-12 h-12 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">AI Intelligence</h3>
            <p className="text-muted-foreground">
              RAG copilot learns from brand guidelines and historical performance.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center space-x-4">
          <Link
            href="/admin"
            className="inline-flex items-center px-6 py-3 rounded-lg bg-secondary text-foreground hover:bg-secondary/80 transition"
          >
            Admin Dashboard
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
          <Link
            href="/campaigns"
            className="inline-flex items-center px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition"
          >
            Campaign Builder
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
        </div>

        {/* Status */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-green-400">Backend Online</span>
          </div>
        </div>
      </div>
    </div>
  )
}
