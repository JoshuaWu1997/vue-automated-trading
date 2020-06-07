<template>
  <div id="trade">
    <div class="chart">
      <div style="height: 5%; position: absolute; left: 70%; top: 0;">
        <header class="time">
          <p>{{ currentTime }}</p>
        </header>
      </div>
      <div style="width: 70%; height: 50%; position: absolute; left: 0; top: 5%;">
        <ve-line :data="chartData" :settings="chartSettings"></ve-line>
      </div>
    </div>
    <div id="portfolio">
      <div style="width: 40%; height: 50%; position: absolute; left: 0; top: 50%;">
        <template>
          <ve-histogram :data="transactionData" :settings="transactionSettings"></ve-histogram>
        </template>
      </div>
      <div style="width: 30%; height: 50%; position: absolute; left: 40%; top: 50%;">
        <template>
          <ve-ring :data="positionData" :settings="positionSettings"></ve-ring>
        </template>
      </div>
    </div>
    <div id="market">
      <div style="width: 30%; height: 95%; position: absolute; left: 70%; top: 5%;">
        <ve-bar :data="marketData" height="100%" :settings="marketSettings"></ve-bar>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Trade',
  data: function () {
    this.transactionSettings = {
      stack: { 'Transaction': ['Buy', 'Sell'] }
    }
    this.chartSettings = {
      min: ['dataMin', 'dataMin'],
      max: ['dataMax', 'dataMax'],
      scale: [true, true]
    }
    this.positionSettings = {
      legendLimit: 0
    }
    this.marketSettings = {
      min: ['dataMin', 'dataMin'],
      max: ['dataMax', 'dataMax'],
      dataOrder: {label: 'buy', order: 'desc'}
    }
    return {
      chartData: {
        columns: ['Time', 'SH50', 'PnL'],
        rows: []
      },
      positionData: {
        columns: ['Target', 'Volume'],
        rows: []
      },
      transactionData: {
        columns: ['Time', 'Buy', 'Sell'],
        rows: []
      },
      marketData: {
        columns: ['stock_id', 'buy', 'sell'],
        rows: []
      },
      ws: null,
      allAlign: null,
      currentTime: 'waiting to start...',
      status: this.$route.params.status,
      id: this.$route.params.id
    }
  },
  created () {
    for (var i = 0; i < 180; i++) {
      this.chartData.rows.push({'Time': '', 'SH50': null, 'PnL': null})
      this.transactionData.rows.push({'Time': '', 'Buy': null, 'Sell': null})
    }
    this.ws = new WebSocket('ws://localhost:12001')
    this.ws.onopen = () => {
      this.ws.send(this.status + ',' + this.id)
    }
    this.ws.onmessage = msg => {
      var msgData = JSON.parse(msg.data)
      this.currentTime = msgData.curr_time
      this.positionData.rows = msgData.position
      this.marketData.rows = msgData.market_info
      this.chartData.rows.shift()
      this.chartData.rows.push({'Time': msgData.curr_time, 'SH50': msgData.sh50, 'PnL': msgData.net_value})
      this.transactionData.rows.shift()
      this.transactionData.rows.push({'Time': msgData.curr_time, 'Buy': msgData.Buy, 'Sell': msgData.Sell})
    }
  }
}
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 5%;
}
.mytable-style .vxe-body--row.row-green {
  background-color: #187;
  color: #fff;
}
.mytable-style .vxe-body--column.col-red {
  background-color: red;
  color: #fff;
}
</style>
