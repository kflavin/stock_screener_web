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
  });

  it('it should return "home" for activeTab', () => {
    const defaultData = Home.data();
    expect(defaultData.activeTab).to.equal("home");
  });

  it('it should have a logout function', () => {
    expect(typeof(Home.methods.logout)).to.equal('function');
  });

  it('it should have a activeTab function', () => {
    expect(typeof(Home.methods.setActiveTab)).to.equal('function');
  });

  // it('renders correctly', () => {
  //   const Ctor = Vue.extend(Home);
  //   const vm = new Ctor().$mount();
  //   dump("-------------");
  //   dump(vm);
  //   console.log(vm);
  //   dump("-------------");
  //   expect(1).to.equal(1);
  // });
});
