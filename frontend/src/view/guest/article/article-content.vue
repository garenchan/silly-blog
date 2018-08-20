<template>
  <div>
    <Card :dis-hover="true">
      <div slot="title">
        <div class="title-box">
          <Avatar :style="{background: avatarColor}">{{ article.source && article.source.name }}</Avatar>
          <span class="title">&nbsp;{{ article.title }}</span>
        </div>
        <div class="info-box">
          <Tooltip :content="publishedTime" placement="bottom">
            <Tag class="published-time" v-if="article.published_at">发表于<Time :time="article.published_at"/></Tag>
          </Tooltip>
          <Tag v-if="article.category">{{ category }}</Tag>
          <Tag :key="tag.id" v-for="tag in article.tags" color="primary">
            <Icon type="ios-pricetags-outline"/>{{ tag.name }}
          </Tag>
          <Tag style="float: right;" v-if="article.stars != undefined">{{ '点赞:' + article.stars }}</Tag>
          <Tag style="float: right;" v-if="article.views != undefined">{{ '阅读:' + article.views }}</Tag>
        </div>
      </div>
      <article v-html="content" class="markdown-body">
      </article>
      <Spin size="large" fix v-if="loading"></Spin>
    </Card>
  </div>
</template>

<script>
import { getArticle } from '@/api/article'
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
  computed: {
    avatarColor () {
      const colorMap = {
        '原创': 'green',
        '转载': 'red',
        '翻译': 'yellow'
      }
      let sourceName = this.article.source && this.article.source.name
      if (sourceName) return colorMap[sourceName] || 'black'
      else return 'white'
    },
    publishedTime () {
      let date = new Date(this.article.published_at || null)
      return date.toLocaleString()
    },
    category () {
      let categories = []
      for (var item of this.article.category) categories.push(item.name)
      return categories.join(' - ')
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
          if (article.category.length) this.$root.$emit('menuChanged', article.category.slice(-1)[0].name)
          this.$root.$emit('articleAuthor', article.user.id)
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

<style lang="less" scoped>
.title-box {
  display: table;
  margin-bottom: 10px;
}
.title {
  font-size: 24px;
  font-weight: bold;
  display : table-cell;
  vertical-align: middle;
}
</style>
