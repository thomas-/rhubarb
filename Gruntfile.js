module.exports = function(grunt) {

  grunt.initConfig({
    less: {
      development: {
        files: [
          {src: 'less/app.less', dest: 'static/app.css'}
        ]
      }
    },
    watch: {
      files: ['less/*.less'],
      tasks: ['less']
    }
  });

  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', ['less']);

};