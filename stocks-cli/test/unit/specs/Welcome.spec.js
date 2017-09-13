import Vue from 'vue'
import Welcome from '@/components/home/Welcome'

function getRenderedText (Component, propsData) {
  const Ctor = Vue.extend(Component);
  const vm = new Ctor().$mount();
  return vm.$el.textContent;
}

describe('Welcome.vue', () => {
  it('renders content correctly', () => {
    console.log(getRenderedText(Welcome));
    expect(getRenderedText(Welcome)).to.equal("This is the welcome page!  Hello.");
  });
});
