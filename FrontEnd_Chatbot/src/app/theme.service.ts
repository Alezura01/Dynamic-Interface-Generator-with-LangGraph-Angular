import { Injectable, Renderer2, RendererFactory2 } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private renderer: Renderer2;
  private linkElement: HTMLLinkElement | null = null;

  constructor(rendererFactory: RendererFactory2) {
    this.renderer = rendererFactory.createRenderer(null, null);
  }

  applyTheme() {
    const href = 'assets/styles/custom-theme.css';

    if (this.linkElement) return;

    const linkEl = this.renderer.createElement('link');
    this.renderer.setAttribute(linkEl, 'rel', 'stylesheet');
    this.renderer.setAttribute(linkEl, 'type', 'text/css');
    this.renderer.setAttribute(linkEl, 'href', href);
    this.renderer.appendChild(document.head, linkEl);

    this.linkElement = linkEl;
  }

  setBodyClass(page: string) {
    document.body.className = '';
    document.body.classList.add(`app-${page}`);
  }
}
