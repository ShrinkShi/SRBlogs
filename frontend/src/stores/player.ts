import { defineStore } from 'pinia'
import type { MusicItem } from '@/types'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    tracks: [] as MusicItem[],
    current: 0,
    playing: false,
    currentTime: 0,
    duration: 0,
    audio: null as HTMLAudioElement | null
  }),
  getters: {
    track: (state) => state.tracks[state.current]
  },
  actions: {
    ensureAudio() {
      if (this.audio || typeof Audio === 'undefined') return
      this.audio = new Audio()
      this.audio.preload = 'metadata'
      this.audio.addEventListener('timeupdate', () => { this.currentTime = this.audio?.currentTime || 0 })
      this.audio.addEventListener('loadedmetadata', () => { this.duration = this.audio?.duration || 0 })
      this.audio.addEventListener('ended', () => { this.next() })
    },
    setTracks(items: MusicItem[]) {
      this.ensureAudio()
      this.tracks = [...items].sort((a, b) => Number(a.sort ?? 0) - Number(b.sort ?? 0))
      if (this.current >= this.tracks.length) this.current = 0
      this.syncAudio(false)
    },
    syncAudio(autoplay?: boolean) {
      this.ensureAudio()
      const track = this.track
      if (!this.audio || !track?.url) return
      if (this.audio.src !== new URL(track.url, window.location.href).href) {
        this.audio.src = track.url
        this.audio.load()
      }
      if (autoplay ?? this.playing) this.play()
    },
    async play() {
      this.ensureAudio()
      const track = this.track
      if (!this.audio || !track?.url) {
        this.playing = false
        return
      }
      this.syncAudio(false)
      try {
        await this.audio.play()
        this.playing = true
      } catch {
        this.playing = false
      }
    },
    pause() {
      this.audio?.pause()
      this.playing = false
    },
    toggle() {
      return this.playing ? this.pause() : this.play()
    },
    next() {
      if (!this.tracks.length) return
      this.current = (this.current + 1) % this.tracks.length
      this.currentTime = 0
      this.duration = 0
      this.syncAudio(this.playing)
    },
    prev() {
      if (!this.tracks.length) return
      this.current = (this.current - 1 + this.tracks.length) % this.tracks.length
      this.currentTime = 0
      this.duration = 0
      this.syncAudio(this.playing)
    },
    seek(value: number) {
      if (!this.audio || !this.duration) return
      this.audio.currentTime = Math.max(0, Math.min(this.duration, value))
    }
  }
})
