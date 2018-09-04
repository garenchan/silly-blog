<template>
  <div>
    <Row>
      <i-col span="6">
        <div class="cover" :style="{'backgroundImage': 'url(' + cover + ')'}"></div>
      </i-col>
      <i-col span="18">
        <div class="info">
          <div>
            <router-link class="title" :to="{ name: 'guest_article', params: { article_id: article.id }}">
              [{{ article.source.name }}] {{ article.title }}
            </router-link>
            <Tag :key="tag.id" v-for="tag in article.tags" color="primary" style="float: right">
              <Icon type="ios-pricetags-outline"/>{{ tag.name }}
            </Tag>
          </div>
          <div class="summary">{{ summary }}</div>
          <div class="extra">
            <Avatar>{{ article.user.name }}</Avatar>
            <Tag>{{ article.user.name }}</Tag>
            <Tag>发表于<Time :time="article.published_at"/></Tag>
            <Tag v-if="category">{{ category }}</Tag>
            <Tag style="float: right; margin-top: 5px">点赞: {{ article.stars }}</Tag>
            <Tag style="float: right; margin-top: 5px">阅读: {{ article.views }}</Tag>
          </div>
        </div>
      </i-col>
    </Row>
  </div>
</template>

<script>
export default {
  name: 'category-article-item',
  props: {
    article: Object
  },
  computed: {
    category () {
      let categories = []
      for (var item of this.article.category) categories.push(item.name)
      return categories.join(' - ')
    },
    summary () {
      const magic = 'cover:'
      let summary = this.article.summary
      let index = summary.toLowerCase().lastIndexOf(magic)
      if (index < 0) return summary
      else return summary.substring(0, index)
    },
    cover () {
      const magic = 'cover:'
      const defaultCover = 'https://file.iviewui.com/iview-live.png'
      let summary = this.article.summary
      let index = summary.toLowerCase().lastIndexOf(magic)
      if (index < 0) return defaultCover
      else return summary.substring(index + magic.length).trim()
    }
  }
}
</script>

<style scoped>
.cover {
  height: 130px;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
}
.info {
  height: 130px;
  padding: 14px;
}
.title {
  font-size: 18px;
  font-weight: bold;
  height: 1em;
  line-height: 1em;
  overflow: hidden;
}
.summary {
  font-size: 15px;
  margin-top: 10px;
  color: #9ea7b4;
  height: 2em;
  line-height: 1em;
  overflow: hidden;
}
.extra {
  margin-top: 10px;
}
</style>
