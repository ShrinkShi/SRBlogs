import { defineStore } from 'pinia'
import type { MusicItem } from '@/types'

export type PlayMode = 'sequence' | 'shuffle' | 'repeat-one'

function songKey(item?: MusicItem) {
  return String(item?.id || item?.title || item?.url || '').trim()
}

function sortTracks(items: MusicItem[]) {
  const normalized = items.map((item) => ({ ...item, likes: Math.max(0, Number(item.likes || 0)) }))
  const hasLikes = normalized.some((item) => Number(item.likes || 0) > 0)
  if (!hasLikes) return normalized.sort((a, b) => Number(a.sort ?? 0) - Number(b.sort ?? 0))
  return normalized.sort((a, b) => {
    const likeDelta = Number(b.likes || 0) - Number(a.likes || 0)
    return likeDelta || Number(a.sort ?? 0) - Number(b.sort ?? 0)
  })
}

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
    playMode: 'sequence' as PlayMode,
    modeLoaded: false,
    likedSongIds: [] as string[],
    likesLoaded: false,
    audio: null as HTMLAudioElement | null
  }),
  getters: {
    track: (state) => state.tracks[state.current]
  },
  actions: {
    songKey,
    ensureAudio() {
      if (this.audio || typeof Audio === 'undefined') return
      this.audio = new Audio()
      this.audio.preload = 'metadata'
      this.loadVolumePreference()
      this.loadModePreference()
      this.loadLikePreference()
      this.applyVolume()
      this.audio.addEventListener('timeupdate', () => { this.currentTime = this.audio?.currentTime || 0 })
      this.audio.addEventListener('loadedmetadata', () => { this.duration = this.audio?.duration || 0 })
      this.audio.addEventListener('ended', () => {
        if (this.playMode === 'repeat-one') {
          if (this.audio) this.audio.currentTime = 0
          this.play()
          return
        }
        this.next()
      })
    },
    setTracks(items: MusicItem[]) {
      this.ensureAudio()
      const previousKey = songKey(this.track)
      this.tracks = sortTracks(items)
      if (previousKey) {
        const nextIndex = this.tracks.findIndex((item) => songKey(item) === previousKey)
        if (nextIndex >= 0) this.current = nextIndex
      }
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
      if (this.playMode === 'repeat-one') {
        this.currentTime = 0
        if (this.audio) this.audio.currentTime = 0
        this.syncAudio(this.playing)
        return
      }
      if (this.playMode === 'shuffle' && this.tracks.length > 1) {
        let nextIndex = this.current
        while (nextIndex === this.current) nextIndex = Math.floor(Math.random() * this.tracks.length)
        this.current = nextIndex
      } else {
        this.current = (this.current + 1) % this.tracks.length
      }
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
    },
    loadModePreference() {
      if (this.modeLoaded || typeof localStorage === 'undefined') return
      const stored = localStorage.getItem('sr-player-mode')
      if (stored === 'sequence' || stored === 'shuffle' || stored === 'repeat-one') this.playMode = stored
      this.modeLoaded = true
    },
    persistModePreference() {
      if (typeof localStorage === 'undefined') return
      localStorage.setItem('sr-player-mode', this.playMode)
    },
    cyclePlayMode() {
      this.playMode = this.playMode === 'sequence' ? 'shuffle' : this.playMode === 'shuffle' ? 'repeat-one' : 'sequence'
      this.persistModePreference()
    },
    setPlayMode(mode: PlayMode) {
      this.playMode = mode
      this.persistModePreference()
    },
    loadLikePreference() {
      if (this.likesLoaded || typeof localStorage === 'undefined') return
      try {
        const stored = JSON.parse(localStorage.getItem('sr-liked-songs') || '[]')
        this.likedSongIds = Array.isArray(stored) ? stored.map(String) : []
      } catch {
        this.likedSongIds = []
      }
      this.likesLoaded = true
    },
    persistLikePreference() {
      if (typeof localStorage === 'undefined') return
      localStorage.setItem('sr-liked-songs', JSON.stringify(this.likedSongIds))
    },
    isLiked(id: string) {
      this.loadLikePreference()
      return this.likedSongIds.includes(id)
    },
    setLikedLocal(id: string, liked: boolean) {
      this.loadLikePreference()
      if (liked && !this.likedSongIds.includes(id)) this.likedSongIds.push(id)
      if (!liked) this.likedSongIds = this.likedSongIds.filter((item) => item !== id)
      this.persistLikePreference()
    },
    updateTrackLikes(id: string, likes: number) {
      const currentKey = songKey(this.track)
      this.tracks = sortTracks(this.tracks.map((item) => songKey(item) === id ? { ...item, likes: Math.max(0, Number(likes || 0)) } : item))
      const index = this.tracks.findIndex((item) => songKey(item) === id)
      if (index >= 0 && songKey(this.track) !== id) {
        const nextIndex = this.tracks.findIndex((item) => songKey(item) === currentKey)
        if (nextIndex >= 0) this.current = nextIndex
      } else if (index >= 0) {
        this.current = index
      }
    }
  }
})
