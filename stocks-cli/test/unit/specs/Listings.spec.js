import Vue from 'vue'
import Listings from '@/components/home/Listings'

function getRenderedText (Component, propsData) {
  const Ctor = Vue.extend(Component);
  const vm = new Ctor().$mount();
  return vm.$el.textContent;
}

describe('Listings.vue', () => {
  it('renders content correctly', () => {
    console.log(getRenderedText(Listings))
    expect(getRenderedText(Listings)).to.equal("Listings")
  });
});
