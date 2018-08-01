<template>
  <div>
    <Card>
      <tables ref="table"
              editable searchable
              search-place="top"
              :loading="loading"
              :toolbox="toolbox"
              v-model="tableData"
              :columns="columns"
              @on-delete="handleDelete"/>
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
import AddTag from './add.vue'
import { getTags } from '@/api/tag'
import { EventBus } from '@/libs/bus'

export default {
  name: 'TagTable',
  components: {
    Tables,
    AddTag
  },
  data () {
    return {
      // 初始化数据总条数
      dataTotal: 0,
      // 分页显示条数默认为10
      pageSize: 10,
      // 当前所在分页索引
      currentPage: 1,
      tableData: [],
      columns: [
        {title: 'Name', key: 'name', editable: true, sortable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Update-Time', key: 'updated_at', sortable: true},
        {
          title: 'Handle',
          key: 'handle',
          options: [],
          button: []
        }
      ],
      loading: false,
      toolbox: {
        'add': AddTag
      }
    }
  },
  methods: {
    getTableData () {
      this.loading = true
      return new Promise((resolve, reject) => {
        getTags({page: this.currentPage, pageSize: this.pageSize}).then(res => {
          this.tableData = res.tags
          this.dataTotal = res.total
          this.loading = false
          resolve()
        }).catch(err => {
          console.log(err)
          // const response = err.response
          // const data = response.data
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
    exportExcel () {
      this.$refs.table.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
    }
  },
  mounted () {
    EventBus.$on('tagCreated', () => {
      this.getTableData()
    })
    this.getTableData()
  }
}
</script>
