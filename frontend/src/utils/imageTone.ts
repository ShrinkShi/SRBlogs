export type ImageTone = 'light' | 'dark'

const cache = new Map<string, ImageTone>()

export async function detectImageTone(source?: string, fallback: ImageTone = 'dark'): Promise<ImageTone> {
  if (!source) return fallback
  if (cache.has(source)) return cache.get(source) || fallback

  try {
    const image = new Image()
    image.crossOrigin = 'anonymous'
    image.decoding = 'async'

    await new Promise<void>((resolve, reject) => {
      image.onload = () => resolve()
      image.onerror = () => reject(new Error('image load failed'))
      image.src = source
    })

    const canvas = document.createElement('canvas')
    const size = 24
    canvas.width = size
    canvas.height = size
    const context = canvas.getContext('2d', { willReadFrequently: true })
    if (!context) throw new Error('canvas context unavailable')

    context.drawImage(image, 0, 0, size, size)
    const data = context.getImageData(0, 0, size, size).data
    let total = 0
    let count = 0
    for (let index = 0; index < data.length; index += 4) {
      const alpha = data[index + 3] / 255
      if (alpha < 0.2) continue
      const luminance = (0.2126 * data[index] + 0.7152 * data[index + 1] + 0.0722 * data[index + 2]) * alpha
      total += luminance
      count += 1
    }

    const tone: ImageTone = count && total / count > 145 ? 'light' : 'dark'
    cache.set(source, tone)
    return tone
  } catch {
    cache.set(source, fallback)
    return fallback
  }
}
