<template>
  <Row>
    <Col class="left-side" :style="{ fontSize: leftFontSize }" :span="leftSideSpan">
      <slot name="left-side"></slot>
    </Col>
    <div class="split" :style="{ left: splitLeft }"></div>
    <Col class="right-side" :style="{ fontSize: rightFontSize }" :span="rightSideSpan">
      <slot name="right-side"></slot>
    </Col>
  </Row>
</template>

<script>
export default {
  name: 'VerticalDivider',
  props: {
    leftSideSpan: {
      type: Number,
      default: 12
    },
    rightSideSpan: {
      type: Number,
      default: 12
    },
    leftFontSize: {
      type: String,
      default: '12px'
    },
    rightFontSize: {
      type: String,
      default: '12px'
    }
  },
  computed: {
    splitLeft: function () {
      let ratio = (this.leftSideSpan) / (this.leftSideSpan + this.rightSideSpan) * 100
      return ratio.toFixed(2) + '%'
    }
  }
}
</script>

<style lang="less">
.left-side {
  padding: 0 10px;
}
.right-side {
  padding: 0 10px;
  position: relative;
  overflow: hidden;
  transition: height .2s ease-in-out;
}
.split {
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  border: 0.5px solid #dddddd;
}
</style>
