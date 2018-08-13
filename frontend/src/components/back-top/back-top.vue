<template>
  <!--<div style="display: none"></div>-->
  <div :class="classes" :style="styles" title="返回顶端" @click="back">
    <slot>
      <div :class="innerClasses">
        <i class="ivu-icon ivu-icon-ios-arrow-up"></i>
      </div>
    </slot>
  </div>
</template>

<script>
import { scrollTop } from 'iview/src/utils/assist'
import { on, off } from 'iview/src/utils/dom'
const prefixCls = 'ivu-back-top'
export default {
  name: 'BackTop',
  props: {
    parentId: {
      type: String,
      default: ''
    },
    parentTagName: {
      type: String,
      default: 'body'
    },
    height: {
      type: Number,
      default: 400
    },
    bottom: {
      type: Number,
      default: 30
    },
    right: {
      type: Number,
      default: 30
    },
    duration: {
      type: Number,
      default: 1000
    }
  },
  data () {
    return {
      backTop: false
    }
  },
  computed: {
    element () {
      let elem = null
      if (this.parentId) elem = document.getElementById(this.parentId)
      if (!elem && this.parentTagName) elem = document.getElementsByTagName(this.parentTagName)[0]
      return elem
    },
    classes () {
      return [
        `${prefixCls}`,
        {
          [`${prefixCls}-show`]: this.backTop
        }
      ]
    },
    styles () {
      return {
        bottom: `${this.bottom}px`,
        right: `${this.right}px`
      }
    },
    innerClasses () {
      return `${prefixCls}-inner`
    }
  },
  methods: {
    handleScroll () {
      let elem = this.element
      if (elem) this.backTop = elem.scrollTop >= this.height
    },
    back () {
      let elem = this.element
      if (elem) {
        scrollTop(elem, elem.scrollTop, 0, this.duration)
        this.$emit('on-click')
      }
    }
  },
  mounted () {
    let elem = this.element
    if (elem) {
      on(elem, 'scroll', this.handleScroll)
      on(elem, 'resize', this.handleScroll)
    } else console.log('warning: backtop parent is null')
  },
  beforeDestroy () {
    let elem = this.element
    if (elem) {
      off(elem, 'scroll', this.handleScroll)
      off(elem, 'resize', this.handleScroll)
    }
  }
}
</script>
