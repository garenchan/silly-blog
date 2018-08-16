<template>
  <div>
    <Card>
      <p slot="title">
        <Icon type="md-flower"/>
        欢迎光临{{ blogName }}
      </p>
      <p>文章总数: 100</p>
      <p>评论总数: 100</p>
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
        <a :href="item.link" class="ad-carouse">
          <img src="@/assets/images/ad.png">
        </a>
      </CarouselItem>
    </Carousel>

  </div>
</template>

<script>
import config from '_conf/config.js'
export default {
  name: 'right-sider',
  data () {
    return {
      blogName: config.blogName,
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
  }
}
</script>

<style scoped>
.ad-carouse {
  height: 200px;
}
</style>
