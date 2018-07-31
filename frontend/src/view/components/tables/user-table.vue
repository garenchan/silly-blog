<template>
  <div>
    <Card>
      <tables ref="tables" editable searchable search-place="top" v-model="tableData" :columns="columns" @on-delete="handleDelete"/>
      <Button style="margin: 10px 0;" type="primary" @click="exportExcel">导出为Csv文件</Button>
    </Card>
  </div>
</template>

<script>
import Tables from '_c/tables'
import { getUsersInfo } from '@/api/user'
export default {
  name: 'user-table',
  components: {
    Tables
  },
  data () {
    return {
      columns: [
        {title: 'Name', key: 'name', sortable: true},
        {title: 'Email', key: 'email', editable: true, sortable: true},
        {title: 'Create-Time', key: 'created_at', sortable: true},
        {
          title: 'Handle',
          key: 'handle',
          options: [],
          button: [
          ]
        }
      ],
      tableData: []
    }
  },
  methods: {
    handleDelete (params) {
      console.log(params)
    },
    exportExcel () {
      this.$refs.tables.exportCsv({
        filename: `table-${(new Date()).valueOf()}.csv`
      })
    }
  },
  mounted () {
    getUsersInfo().then(res => {
      this.tableData = res.users
    })
  }
}
</script>

<style>

</style>
