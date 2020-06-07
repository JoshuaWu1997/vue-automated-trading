<template>
  <div id="list">
    <h1>Trade List</h1>
    <vxe-table
      border
      show-header-overflow
      show-overflow
      highlight-hover-row
      :align="allAlign"
      :data="tableData"
      @cell-dblclick="cellDBLClickEvent"
    >
      <vxe-table-column type="seq" field="t_id" width="60"></vxe-table-column>
      <vxe-table-column
        field="begin_datetime"
        title="Start Time"
      ></vxe-table-column>
      <vxe-table-column
        field="end_datetime"
        title="End Time"
      ></vxe-table-column>
      <vxe-table-column
        field="begin_cash"
        title="Initial Cash"
      ></vxe-table-column>
      <vxe-table-column
        field="valid_cash"
        title="Current Cash"
      ></vxe-table-column>
      <vxe-table-column
        field="total_asset"
        title="Total Asset"
      ></vxe-table-column>
      <vxe-table-column
        field="trade_state"
        title="Status"
        width="100"
      ></vxe-table-column>
    </vxe-table>
  </div>
</template>

<script>
export default {
  name: 'List',
  data () {
    return {
      allAlign: null,
      tableData: []
    }
  },
  created () {
    var ws = new WebSocket('ws://localhost:12000')
    // Get Trade List Data and Convert to JSON
    ws.onmessage = msg => {
      this.tableData = JSON.parse(msg.data)
      console.log(JSON.parse(msg.data))
    }
  },
  methods: {
    // Double Click on the Cell
    cellDBLClickEvent ({ rowIndex }) {
      this.$router.push({
        name: 'Trade',
        params: {
          status: this.tableData[rowIndex].trade_state,
          id: this.tableData[rowIndex].t_id
        }
      })
    }
  }
}
</script>

<style></style>
