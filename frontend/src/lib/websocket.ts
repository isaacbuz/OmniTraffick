"use client"

import { useEffect, useRef } from "react"
import { useQueryClient } from "@tanstack/react-query"
import io, { Socket } from "socket.io-client"

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001"

export function useWebSocket() {
  const queryClient = useQueryClient()
  const socketRef = useRef<Socket | null>(null)

  useEffect(() => {
    // Connect to WebSocket
    const socket = io(WS_URL, {
      transports: ["websocket"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    })

    socketRef.current = socket

    // Connection events
    socket.on("connect", () => {
      console.log("🔌 WebSocket connected")
    })

    socket.on("disconnect", () => {
      console.log("🔌 WebSocket disconnected")
    })

    // Ticket status updates
    socket.on("ticket:status_changed", (data: any) => {
      console.log("📨 Ticket status update:", data)
      
      // Invalidate queries to refetch
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
      queryClient.invalidateQueries({ queryKey: ["campaigns"] })
    })

    // Deployment events
    socket.on("deployment:started", (data: any) => {
      console.log("🚀 Deployment started:", data)
    })

    socket.on("deployment:completed", (data: any) => {
      console.log("✅ Deployment completed:", data)
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    })

    socket.on("deployment:failed", (data: any) => {
      console.log("❌ Deployment failed:", data)
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    })

    // Cleanup
    return () => {
      socket.disconnect()
    }
  }, [queryClient])

  return socketRef.current
}
