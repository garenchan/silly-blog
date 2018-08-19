<template>
  <div>
    <Card :dis-hover="true">
      <div>
        <Avatar style="background-color: #f56a00">{{ article.source && article.source.name }}</Avatar>
        <span class="title">&nbsp;{{ article.title }}</span>
      </div>
      <Divider />
      <article v-html="content" class="markdown-body">
      </article>
      <Spin size="large" fix v-if="loading"></Spin>
    </Card>
  </div>
</template>

<script>
import { getArticle } from '@/api/article'
import { EventBus } from '@/libs/bus'
// import showdown from 'showdown'
import marked from 'marked'
import hljs from 'highlight.js'
import '@/styles/markdown.less'

export default {
  name: 'article-content',
  data () {
    return {
      id: this.$route.params.article_id,
      article: {},
      content: '',
      loading: false
      // converter: null
    }
  },
  methods: {
    renderMd (md) {
      const renderer = new marked.Renderer()
      return marked(md, {
        breaks: true,
        gfm: true,
        headerIds: true,
        highlight: (code) => {
          return hljs.highlightAuto(code).value
        },
        tables: true,
        renderer
      })
    },
    getCurrentArticle () {
      return new Promise((resolve, reject) => {
        this.loading = true
        getArticle(this.id).then(res => {
          this.loading = false
          let article = this.article = res.article
          // this.content = this.converter.makeHtml(article.content)
          this.content = this.renderMd(article.content)
          // 更新顶部导航栏
          if (article.category.length) EventBus.$emit('menuChanged', article.category.slice(-1)[0].name)
        }).catch(err => {
          this.loading = false
          console.log('load current article failed:' + err)
        })
      })
    }
  },
  mounted () {
    /* this.converter = new showdown.Converter({
      omitExtraWLInCodeBlocks: true,
      parseImgDimensions: true,
      simplifiedAutoLink: true,
      strikethrough: true,
      tables: true,
      tasklists: true,
      smartIndentationFix: true,
      simpleLineBreaks: true,
      // ghCodeBlocks: true,
      ghMentions: true,
      openLinksInNewWindow: true,
      emoji: true,
      underline: true,
      splitAdjacentBlockquotes: true
    })
    this.converter.setFlavor('github') */
    this.getCurrentArticle()
  }
}
</script>

<style lang="less">
.title {
  font-size: 20px;
  font-weight: bold;
}
</style>
