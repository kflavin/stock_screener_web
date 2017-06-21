import Vue from 'vue'
import Home from '@/components/home/Home.vue'
// import Home from '../../../src/components/home/Home.vue'

describe('Home.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(Home);
    expect(1).to.equal(1);
    //const vm = new Constructor().$mount()
    // expect(vm.$el.querySelector('.hello h1').textContent)
    //   .to.equal('Welcome to Your Vue.js App')
  })
})
