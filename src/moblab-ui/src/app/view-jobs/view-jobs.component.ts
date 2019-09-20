import {Component, OnInit} from '@angular/core';
import {MoblabGrpcService} from '../services/moblab-grpc.service';


@Component({
  selector: 'app-view-jobs',
  templateUrl: './view-jobs.component.html',
  styleUrls: ['./view-jobs.component.css']
})
export class ViewJobsComponent implements OnInit {
  helloText = 'Not set yet';
  constructor(private moblabGrpcService: MoblabGrpcService) {}


  ngOnInit() {
    this.moblabGrpcService.runSuite('World', (newText: string) => {
      this.helloText = newText;
    });
  }
}
