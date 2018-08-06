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
              @on-sort-change="handleSortChange"
              @on-save-edit="handleEdit"
              :custom-search="true"
              @on-search="handleSearch"
              @on-delete="handleDelete"
              @on-state-change="handleStateChange"/>
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
import AddUser from './add.vue'
import { listUsers, updateUser, deleteUser } from '@/api/user'
import { EventBus } from '@/libs/bus'

export default {
  name: 'UserTable',
  components: {
    Tables,
    AddUser
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
        // {type: 'selection', key: 'id', width: 60, align: 'center'},
        {title: 'Name', key: 'name', editable: true, sortable: true, searchable: true},
        // {title: 'Nickname', key: 'display_name', editable: true, sortable: true, searchable: true},
        {title: 'Email', key: 'email', editable: true, sortable: true, searchable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {title: 'Update-Time', key: 'updated_at', sortable: true, sortType: 'desc'},
        {
          title: 'Enabled',
          key: 'enabled',
          sortable: false,
          render: (h, params) => {
            return h('i-switch', {
              props: {
                // type: 'primary',
                size: 'large',
                value: params.row.enabled,
                loading: false,
                disabled: this.$store.state.user.id === params.row.id
              },
              on: {
                'on-change': (value) => {
                  this.$refs.table.$emit('on-state-change', Object.assign(params, {value: value}))
                }
              }
            }, [
              h('span', {
                slot: 'open'
              }, '激活'),
              h('span', {
                slot: 'close'
              }, '禁用')
            ])
          }
        },
        {
          title: 'Handle',
          key: 'handle',
          // options: ['delete'],
          button: [
            (h, params, vm) => {
              let name = params.row.name
              return h('Poptip', {
                props: {
                  confirm: true,
                  title: `你确定要删除用户"${name}"吗?`
                },
                on: {
                  'on-ok': () => {
                    vm.$emit('on-delete', params)
                  }
                }
              }, [
                h('Button', {
                  props: {
                    type: 'dashed',
                    icon: 'md-trash',
                    disabled: this.$store.state.user.id === params.row.id
                  }
                }, '删除用户')
              ])
            }
          ]
        }
      ],
      loading: false,
      toolbox: {
        'add': AddUser
      }
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
        listUsers(params).then(res => {
          this.tableData = res.users
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
      let id = params.row.id
      let name = params.row.name
      this.loading = true
      return new Promise((resolve, reject) => {
        deleteUser(id).then(res => {
          this.loading = false
          this.$Message.info(`用户${name}删除成功`)
          this.getTableData()
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if ([404].includes(response.status)) {
            this.$Message.info(`用户${name}删除成功`)
            this.getTableData()
          } else {
            this.$Message.error(data.error.message)
          }
        })
      })
    },
    exportExcel () {
      this.$refs.table.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
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
      let id = params.row.id
      let key = params.column.key
      let origValue = params.row[key]
      let curValue = params.value
      let data = {
        [key]: curValue
      }
      let keyMap = {
        name: '用户名',
        email: '邮箱'
      }
      this.loading = true
      return new Promise((resolve, reject) => {
        updateUser(id, data).then(res => {
          this.loading = false
          this.$Message.info('用户编辑成功')
          this.$set(this.tableData[params.index], key, res.user[key])
          this.$set(this.tableData[params.index], 'updated_at', res.user.updated_at)
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          if (response.status === 409) {
            this.$Message.error(`${keyMap[key]}${curValue}已存在`)
          } else {
            this.$Message.error(data.error.message)
          }
          this.$set(this.tableData[params.index], key, origValue)
        })
      })
    },
    handleStateChange (params) {
      let id = params.row.id
      let origValue = params.row.enabled
      let curValue = params.value
      if (origValue === curValue) return
      let name = params.row.name
      let action = curValue ? '激活' : '禁用'
      this.loading = true
      return new Promise((resolve, reject) => {
        updateUser(id, {enabled: curValue}).then(res => {
          this.loading = false
          this.$Message.info(`用户"${name}"${action}成功`)
          this.$set(this.tableData[params.index], 'enabled', res.user.enabled)
          resolve()
        }).catch(err => {
          this.loading = false
          const response = err.response
          const data = response.data
          this.$Message.error(data.error.message)
          // TODO: while request failed, restore switch
          this.$set(this.tableData[params.index], 'enabled', origValue)
          reject(err)
        })
      })
    }
  },
  mounted () {
    EventBus.$on('userCreated', () => {
      this.getTableData()
    })
    this.getTableData()
  }
}
</script>
