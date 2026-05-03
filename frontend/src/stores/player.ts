import { defineStore } from 'pinia'
import type { MusicItem } from '@/types'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    tracks: [] as MusicItem[],
    current: 0,
    playing: false,
    currentTime: 0,
    duration: 0,
    volume: 0.72,
    muted: false,
    volumeLoaded: false,
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
      this.loadVolumePreference()
      this.applyVolume()
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
      this.applyVolume()
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
    },
    loadVolumePreference() {
      if (this.volumeLoaded || typeof localStorage === 'undefined') return
      const storedVolume = Number(localStorage.getItem('sr-player-volume'))
      const storedMuted = localStorage.getItem('sr-player-muted')
      if (Number.isFinite(storedVolume)) this.volume = Math.max(0, Math.min(1, storedVolume))
      if (storedMuted !== null) this.muted = storedMuted === 'true'
      this.volumeLoaded = true
    },
    persistVolumePreference() {
      if (typeof localStorage === 'undefined') return
      localStorage.setItem('sr-player-volume', String(this.volume))
      localStorage.setItem('sr-player-muted', String(this.muted))
    },
    applyVolume() {
      if (!this.audio) return
      this.audio.volume = this.muted ? 0 : Math.max(0, Math.min(1, this.volume))
    },
    setVolume(value: number) {
      this.volume = Math.max(0, Math.min(1, Number.isFinite(value) ? value : this.volume))
      this.muted = this.volume <= 0
      this.applyVolume()
      this.persistVolumePreference()
    },
    toggleMuted() {
      this.muted = !this.muted
      this.applyVolume()
      this.persistVolumePreference()
    }
  }
})
