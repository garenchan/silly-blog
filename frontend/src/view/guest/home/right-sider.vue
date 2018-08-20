<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="md-flower"/>
        欢迎光临{{ blogName }}
      </p>
      <p>用户总数: {{ userCount }}</p>
      <p>文章总数: {{ articleCount }}</p>
    </Card>
    <Card style="margin-top: 20px">
      <p slot="title">
        <Icon type="md-megaphone"/>
        公告栏
      </p>
      <p>暂无公告</p>
    </Card>
    <Carousel style="margin-top: 20px" autoplay :autoplay-speed="15000" loop>
      <CarouselItem :key="item.link" v-for="item in ads">
        <a :href="item.link" target="_blank" class="ad-carouse">
          <img src="@/assets/images/ad.png">
        </a>
      </CarouselItem>
    </Carousel>
  </div>
</template>

<script>
import config from '_conf/config'
import { listUsers } from '@/api/user'
import { listArticles } from '@/api/article'

export default {
  name: 'right-sider',
  data () {
    return {
      blogName: config.blogName,
      userCount: 0,
      articleCount: 0,
      ads: [
        {
          link: 'http://www.baidu.com',
          image: '@/assets/images/ad.png'
        },
        {
          link: 'http://www.baidu1.com',
          image: '@/assets/images/logo.png'
        }
      ]
    }
  },
  methods: {
    getUserCount () {
      return new Promise((resolve, reject) => {
        listUsers({}).then(res => {
          this.userCount = res.total
        }).catch(err => {
          console.log('load user count failed:' + err)
        })
      })
    },
    getArticleCount () {
      return new Promise((resolve, reject) => {
        listArticles({}).then(res => {
          this.articleCount = res.total
        }).catch(err => {
          console.log('load article count failed:' + err)
        })
      })
    }
  },
  mounted () {
    this.getUserCount()
    this.getArticleCount()
  }
}
</script>

<style scoped>
.ad-carouse {
  height: 200px;
}
</style>
