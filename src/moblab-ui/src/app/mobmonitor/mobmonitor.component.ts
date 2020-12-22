import {Component, OnInit} from '@angular/core';
import {
  ElementRef,
  Pipe,
  PipeTransform,
  ViewChild,
  ViewEncapsulation,
} from '@angular/core';
import {DomSanitizer} from '@angular/platform-browser';

@Pipe({name: 'safe'})
export class MobmonitorPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}
  transform(url) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

@Component({
  selector: 'app-mob-mobmonitor',
  templateUrl: './mobmonitor.component.html',
  styleUrls: ['./mobmonitor.component.scss'],
})
export class MobmonitorComponent {
  title = 'app';

  video = 'http://localhost:9991';
}
