<template>
  <div>
    <Card>
      <tables ref="table"
              editable searchable
              search-place="top"
              :loading="loading"
              v-model="tableData"
              :columns="columns"
              @on-sort-change="handleSortChange"
              @on-save-edit="handleEdit"
              :custom-search="true"
              @on-search="handleSearch">
        <AddArticle slot="toolbox"/>
      </tables>
      <div style="margin: 10px;overflow: hidden">
        <div style="float: right;">
            <Page :total="dataTotal" :page-size="pageSize" :current="currentPage" @on-change="changePage"></Page>
        </div>
      </div>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import AddArticle from './add.vue'
import { listArticles } from '@/api/article'
import { EventBus } from '@/libs/bus'

export default {
  name: 'ArticleTable',
  components: {
    Tables,
    AddArticle
  },
  data () {
    return {
      // 初始化数据总条数
      dataTotal: 0,
      // 分页显示条数默认为10
      pageSize: 10,
      // 当前所在分页索引
      currentPage: 1,
      // sort related
      sortColumn: 'updated_at',
      SortDirection: 'desc',
      // filter related
      searchKey: '',
      searchValue: '',
      tableData: [],
      columns: [
        {title: 'Title', key: 'title', width: 160, editable: true, sortable: true, searchable: true},
        {title: 'Source', key: 'source', sortable: true},
        {title: 'Tags', key: 'tags'},
        {title: 'Author', key: 'user', searchable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Update-Time', key: 'updated_at', sortable: true}
      ],
      loading: false
    }
  },
  methods: {
    getTableData () {
      this.loading = true
      let params = {
        page: this.currentPage,
        pageSize: this.pageSize,
        sort: this.sortColumn,
        direction: this.SortDirection
      }
      if (this.searchKey) params[this.searchKey] = this.searchValue
      return new Promise((resolve, reject) => {
        listArticles(params).then(res => {
          this.tableData = res.articles
          this.dataTotal = res.total
          this.loading = false
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
        })
      })
    },
    changePage (index) {
      this.currentPage = index
      this.getTableData()
    },
    handleDelete (params) {
      console.log(params)
    },
    handleSortChange ({column, key, order}) {
      this.sortColumn = key
      this.SortDirection = order
      this.getTableData()
    },
    handleSearch ({key, value}) {
      this.searchKey = key
      this.searchValue = value
      this.getTableData()
    },
    handleEdit (params) {
      console.log(params)
    }
  },
  mounted () {
    EventBus.$on('articleCreated', () => {
      this.getTableData()
    })
    this.getTableData()
  }
}
</script>
