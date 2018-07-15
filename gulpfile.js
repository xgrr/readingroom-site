'use strict';

// Include Gulp & Tools We'll Use
var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var del = require('del');
var runSequence = require('run-sequence');
var browserSync = require('browser-sync');
var pagespeed = require('psi');
var browserify = require('gulp-browserify');
var reload = browserSync.reload;

gulp.task('scripts', function() {
  var sources = [
    'node_modules/es6-promise/dist/es6-promise.js',
    'app/scripts/*.js'];

  return gulp.src(sources)
    .pipe($.concat('main.min.js'))
    .pipe(browserify({
          insertGlobals : true,
          debug : true
        }))
    .pipe($.uglify({preserveComments: 'some'}))
    // Output Files
    .pipe(gulp.dest('static/home/js/sw/'))
    .pipe($.size({title: 'scripts'}));
});



// Copy All Filescopy-workerscripts At The Root Level (app)
gulp.task('copy-workerscripts', function() {
  return gulp.src('app/scripts/jsqrcode/*.js')
    .pipe(gulp.dest('static/home/js/sw/jsqrcode/'))
    .pipe($.size({title: 'copy-workerscripts'}));
});

gulp.task('clean', del.bind(null, ['.tmp', 'static/home/js/sw/*', '!static/home/js/sw/.git'], {dot: true}));

gulp.task('pagespeed', pagespeed.bind(null, {
  // By default, we use the PageSpeed Insights
  // free (no API key) tier. You can use a Google
  // Developer API key if you have one. See
  // http://goo.gl/RkN0vE for info key: 'YOUR_API_KEY'
  url: 'https://xananagusmaoreadingroom.com',
  strategy: 'mobile'
}));

gulp.task('copy', function() {
  return gulp.src([
    'app/*',
    
  ], {
    dot: true
  }).pipe(gulp.dest('xanana/templates/'))
    .pipe($.size({title: 'copy'}));
});

// Build Production Files, the Default Task
gulp.task('default', ['clean'], function(cb) {
  runSequence('scripts', ['scripts',  'copy', 'copy-workerscripts'], cb);});


