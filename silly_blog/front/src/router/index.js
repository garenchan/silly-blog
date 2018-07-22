import Vue from 'vue';
import Router from 'vue-router';
// import HelloWorld from '@/components/HelloWorld'
import MyFirst from '@/components/MyFirst';

Vue.use(Router);

export default new Router({
    routes: [
        {
            path: '/',
            // name: 'HelloWorld',
            // component: HelloWorld
            name: 'MyFirst',
            component: MyFirst
        }
    ]
});
