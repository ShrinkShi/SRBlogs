import { computed, unref, watchEffect, type MaybeRefOrGetter } from 'vue'

interface SeoInput {
  title: MaybeRefOrGetter<string>
  siteName?: MaybeRefOrGetter<string | undefined>
  description?: MaybeRefOrGetter<string | undefined>
  image?: MaybeRefOrGetter<string | undefined>
  type?: MaybeRefOrGetter<string | undefined>
  path?: MaybeRefOrGetter<string | undefined>
}

const siteName = 'SRBlogs'
const fallbackDescription = 'SRBlogs - Vue3 + FastAPI personal blog'
const fallbackImage = '/favicon.ico'

function valueOf<T>(value: MaybeRefOrGetter<T>): T {
  return typeof value === 'function' ? (value as () => T)() : unref(value)
}

function ensureMeta(selector: string, attrs: Record<string, string>) {
  let element = document.head.querySelector<HTMLMetaElement>(selector)
  if (!element) {
    element = document.createElement('meta')
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value)
    document.head.appendChild(element)
  }
  return element
}

function absoluteUrl(pathOrUrl: string) {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl
  const origin = window.location?.origin || 'http://127.0.0.1:5173'
  return new URL(pathOrUrl || '/', origin).toString()
}

export function useSeo(input: SeoInput) {
  const titleText = computed(() => {
    const raw = valueOf(input.title)?.trim() || siteName
    const suffix = input.siteName === undefined ? siteName : valueOf(input.siteName)?.trim()
    if (!suffix || raw.includes(suffix)) return raw
    return `${raw} · ${suffix}`
  })

  watchEffect(() => {
    const title = titleText.value
    const description = valueOf(input.description || fallbackDescription)?.trim() || fallbackDescription
    const image = absoluteUrl(valueOf(input.image || fallbackImage) || fallbackImage)
    const path = valueOf(input.path || window.location.pathname) || window.location.pathname
    const url = absoluteUrl(path)
    const type = valueOf(input.type || 'website') || 'website'

    document.title = title
    ensureMeta('meta[name="description"]', { name: 'description' }).content = description
    ensureMeta('meta[property="og:title"]', { property: 'og:title' }).content = title
    ensureMeta('meta[property="og:description"]', { property: 'og:description' }).content = description
    ensureMeta('meta[property="og:type"]', { property: 'og:type' }).content = type
    ensureMeta('meta[property="og:url"]', { property: 'og:url' }).content = url
    ensureMeta('meta[property="og:image"]', { property: 'og:image' }).content = image
    ensureMeta('meta[name="twitter:card"]', { name: 'twitter:card' }).content = 'summary_large_image'
    ensureMeta('meta[name="twitter:title"]', { name: 'twitter:title' }).content = title
    ensureMeta('meta[name="twitter:description"]', { name: 'twitter:description' }).content = description
    ensureMeta('meta[name="twitter:image"]', { name: 'twitter:image' }).content = image
  })
}
