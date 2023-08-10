/*-------- Create Repo ---------------*/
// get file 
var jsonList
$(document).on('change', '.add-repolist', function(event) {
  var reader = new FileReader();

  reader.onload = function(event) {
    jsonList = JSON.parse(event.target.result);
    console.log(jsonList);
  }

  reader.readAsText(event.target.files[0]);
});

// append to form
$(document).on('click', '.btn-upload-jsonlist', function(e) {
  for (var i=0; i<jsonList.length; i++){
    console.log(jsonList.length)
    repo = jsonList[i];
    var currentVal = $("#json-list").val();
    if (i>0) {
      currentVal = currentVal + ",\n";
    }
    $("#json-list").val(currentVal + JSON.stringify(repo, undefined, 2));
  }
});

// additional option
$(document).on('change', '#readme-switch', function(e) {
  var value = $('#readme-switch').is(':checked');
  console.log(value)
  if (value) {
    $('#create-repo-addition').removeClass('d-none');
    $('#create-repo-addition').addClass('d-block');
  }
  else {
    $('#create-repo-addition').removeClass('d-block');
    $('#create-repo-addition').addClass('d-none');
  }
})

/*-------- Create Branch ---------------*/
// select all repo
$(document).on('click', '#cb-selectAll', function(e) {
  $('.cb-select').prop('checked', $(this).prop("checked"));
})

// create branch
$(document).on('click', '.btn-create-branch', function(e) {
  var repos = [];
  var branch = $("table").attr("data-branch");
  console.log(branch);
  $('.cb-select').each(function(i, obj) {
    // console.log($('.cb-select'))
    if ($(this).is(':checked')) {
      repo = $(this).parent().prev("td").text()
      repos.push(repo)
    }
  })  
  // console.log(repos.length)
  if (repos.length <= 0) {
    $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
    <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
    [ERR] Please choose a repo!\
    </div>")
  }
  else {
    var request = $.post({
      url: $(location).attr('href') + 'create',
      data: {
        branch: branch,
        repos: repos
      },
      success: () => {
        $(".alert-msg").append("<div class='alert alert-info alert-dismissible'>\
        <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
        Create successfully!\
        </div>")
        setTimeout(function(){
          location.reload();
        }, 3000);
      },
      error: () => {
        $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
        <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
        [ERR] Something is wrong!\
        </div>")
      }
    });
    console.log(request)
  }
})

/*-------- Add Teams ---------------*/
// select all teams
$(document).on('click', '#atr-at-selectAll', function(e) {
  $('.atr-at-select').prop('checked', $(this).prop("checked"));
})

// select all members
$(document).on('click', '#atr-am-selectAll', function(e) {
  $('.atr-am-select').prop('checked', $(this).prop("checked"));
})

// clear all default teams
$(document).on('click', '.btn-clear-def-teams', function(e) {
  var request = $.post({
    url: $(location).attr('href') + '/clear_all_def_teams',
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      Clear successfully!\
      </div>")
    },
    error: () => {
      $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      [ERR] Something is wrong!\
      </div>")
    }
  });
  console.log(request)
})

// add to default teams
$(document).on('click', '.btn-add-def-teams', function(e) {
  var teams = [];
  $('.at-select').each(function(i, obj) {
    // console.log($('.cb-select'))
    if ($(this).is(':checked')) {
      var team = {
        'name': $(this).parent().siblings('.team-name').text(),
        'permission': $(this).parent().siblings('.team-permission').text()
      }
      console.log(team)
      teams.push(team)
    }
  })  
  if (teams.length <= 0) {
    $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
    <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
    [ERR] Please choose a team!\
    </div>")
  }
  else {
    var request = $.post({
      url: $(location).attr('href') + '/add_def_teams',
      data: {
        def_teams: teams
      },
      success: () => {
        $(".alert-msg").append("<div class='alert alert-info alert-dismissible'>\
        <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
        Added successfully!\
        </div>")
      },
      error: () => {
        $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
        <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
        [ERR] Something is wrong!\
        </div>")
      }
    });
    console.log(request)
  }
})

$(document).on('click', '.clear-invitation', function(e) {
  var invitation_id = $(this).parent().parent().parent().data("id")
  var request = $.post({
    url: $(location).attr('href') + '/clear_invitation',
    data: {
      invitation_id: invitation_id
    },
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      Cancel successfully!\
      </div>")
      setTimeout(function(){
        location.reload();
      }, 500);
    },
    error: () => {
      $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      [ERR] Something is wrong!\
      </div>")
    }
  });
  console.log(request)
})

/*----------- Custom Display -------------*/