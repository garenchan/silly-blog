<template>
  <div class="markdown-wrapper">
    <textarea ref="editor"></textarea>
  </div>
</template>

<script>
import Simplemde from 'simplemde'
import marked from 'marked'
import 'simplemde/dist/simplemde.min.css'
export default {
  name: 'MarkdownEditor',
  props: {
    value: {
      type: String,
      default: ''
    },
    options: {
      type: Object,
      default: () => {
        return {}
      }
    },
    localCache: {
      type: Boolean,
      default: true
    },
    previewClass: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      editor: null
    }
  },
  methods: {
    addEvents () {
      this.editor.codemirror.on('change', () => {
        let value = this.editor.value()
        if (this.localCache) localStorage.markdownContent = value
        this.$emit('input', value)
        this.$emit('on-change', value)
      })
      this.editor.codemirror.on('focus', () => {
        this.$emit('on-focus', this.editor.value())
      })
      this.editor.codemirror.on('blur', () => {
        this.$emit('on-blur', this.editor.value())
      })
    },
    addPreviewClass (className) {
      const wrapper = this.editor.codemirror.getWrapperElement()
      const preview = document.createElement('div')
      wrapper.nextSibling.className += ` ${className}`
      preview.className = `editor-preview ${className}`
      wrapper.appendChild(preview)
    }
  },
  mounted () {
    marked.setOptions({ sanitize: false })
    this.editor = new Simplemde(Object.assign(this.options, {
      element: this.$refs.editor,
      initialValue: this.value
    }))
    // 添加自定义 previewClass
    const className = this.previewClass || ''
    this.addPreviewClass(className)
    /**
     * 事件列表为Codemirror编辑器的事件，更多事件类型，请参考：
     * https://codemirror.net/doc/manual.html#events
     */
    this.addEvents()
    let content = localStorage.markdownContent
    if (content && this.localCache) this.editor.value(content)
  },
  watch: {
    value (val) {
      if (val === this.editor.value()) return
      this.editor.value(val)
    }
  }
}
</script>

<style lang="less">
.markdown-wrapper{
  .editor-toolbar.fullscreen{
    z-index: 9999;
  }
  .CodeMirror-fullscreen{
    z-index: 9999;
  }
  .CodeMirror-fullscreen ~ .editor-preview-side{
    z-index: 9999;
  }
}
</style>
