import Vue from 'vue'
import Router from 'vue-router'
import List from '@/components/List'
import Trade from '@/components/Trade'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'List',
      component: List
    },
    {
      path: '/trade',
      name: 'Trade',
      component: Trade
    }
  ]
})
