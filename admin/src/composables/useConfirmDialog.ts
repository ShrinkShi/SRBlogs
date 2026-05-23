import { reactive } from 'vue'

export type ConfirmDialogVariant = 'danger' | 'default'

export interface ConfirmDialogState {
  open: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  variant: ConfirmDialogVariant
}

type ConfirmDialogOptions = Partial<Omit<ConfirmDialogState, 'open'>> & {
  title: string
  message: string
}

export function useConfirmDialog() {
  const state = reactive<ConfirmDialogState>({
    open: false,
    title: '',
    message: '',
    confirmText: '确认',
    cancelText: '取消',
    variant: 'default'
  })
  let resolveCurrent: ((value: boolean) => void) | null = null

  function ask(options: ConfirmDialogOptions) {
    if (resolveCurrent) resolveCurrent(false)
    Object.assign(state, {
      open: true,
      confirmText: '确认',
      cancelText: '取消',
      variant: 'default' as ConfirmDialogVariant,
      ...options
    })
    return new Promise<boolean>((resolve) => {
      resolveCurrent = resolve
    })
  }

  function close(value: boolean) {
    state.open = false
    resolveCurrent?.(value)
    resolveCurrent = null
  }

  return {
    state,
    ask,
    confirm: () => close(true),
    cancel: () => close(false)
  }
}
