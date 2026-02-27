"use client"

import { useEffect } from "react"

interface MetaPixelProps {
  pixelId: string
  enabled?: boolean
}

export function MetaPixel({ pixelId, enabled = true }: MetaPixelProps) {
  useEffect(() => {
    if (!enabled || !pixelId) return

    // Initialize Meta Pixel
    const script = `
      !function(f,b,e,v,n,t,s)
      {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s)}(window, document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', '${pixelId}');
      fbq('track', 'PageView');
    `

    const scriptElement = document.createElement("script")
    scriptElement.innerHTML = script
    document.head.appendChild(scriptElement)

    return () => {
      document.head.removeChild(scriptElement)
    }
  }, [pixelId, enabled])

  return null
}

interface TrackEventProps {
  eventName: string
  eventId?: string
  parameters?: Record<string, any>
}

export function useMetaTracking() {
  const trackEvent = ({ eventName, eventId, parameters }: TrackEventProps) => {
    if (typeof window === "undefined" || !(window as any).fbq) return

    const options: any = {}
    if (eventId) {
      options.eventID = eventId
    }

    ;(window as any).fbq("track", eventName, parameters || {}, options)

    // Also send to backend for CAPI
    fetch("/api/v1/tracking/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_name: eventName,
        event_id: eventId || generateEventId(),
        user_data: {
          client_ip_address: "", // Filled server-side
          client_user_agent: navigator.userAgent,
          fbc: getCookie("_fbc"),
          fbp: getCookie("_fbp"),
        },
        custom_data: parameters,
        event_source_url: window.location.href,
      }),
    }).catch(console.error)
  }

  return { trackEvent }
}

function generateEventId(): string {
  return `${Date.now()}_${Math.random().toString(36).slice(2)}`
}

function getCookie(name: string): string | undefined {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(";").shift()
}
