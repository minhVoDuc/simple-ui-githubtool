const error_pattern = /(<p>)(.+)(<\/p>)/

$(document).on('click', 'th .selectAll', function(e) {
  var trs = $(this).parents("table").children("tbody").children("tr");
  console.log(trs.children("td").children(".selectItem"))
  trs.children("td").children(".selectItem").prop('checked', $(this).prop("checked"));
})

/*-------- Indexing -----------------*/
// clear all default teams
$(document).on('click', '.btn-clear-def-teams', function(e) {
  var request = $.post({
    url: $(location).attr('href') + '/clear_all_def_teams',
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info'>\
      Clear successfully!\
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

// add to default teams
$(document).on('click', '.btn-add-def-team', function(e) {
  var team = $("#index_teamlist :selected").val()
  var request = $.post({
    url: $(location).attr('href') + '/add_def_team',
    data: {
      team: team
    },
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info'>\
      Added successfully!\
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

// append to text area
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
        $(".alert-msg").append("<div class='alert alert-info'>\
        Create successfully!\
        </div>")
        setTimeout(function(){
          location.reload();
        }, 1000);
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

/*-------- Collaborator ---------------*/
$(document).on('click', '.clear-invitation', function(e) {
  var invitation_id = $(this).parent().parent().parent().data("id")
  var request = $.post({
    url: $(location).attr('href') + '/clear_invitation',
    data: {
      invitation_id: invitation_id
    },
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info'>\
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

// select team in a repo
$(document).on('click', '.repo_team tbody tr', function(e) {
  console.log("team slug: "+$(this).data('slug'))
  if ($(this).hasClass('table-active')){
    $(this).removeClass('table-active')
  }
  else {
    $(this).addClass('table-active');
  }
});

// get selected team
function get_selected_teams(table) {
  selected_teams = []
  table.children("tbody").children().each(function() {
    if ($(this).hasClass("table-active")) {
      selected_teams.push($(this).data("slug"))
    }
  })
  console.log(selected_teams)
  return selected_teams
}

// remove teams from repo
$(document).on('click', '.btn-rmv-team-repo', function(e) {
  var table = $(this).siblings("table")
  var selected_teams = get_selected_teams(table)
  var request = $.post({
    url: $(location).attr('href') + '/remove_repo_teams',
    data: {
      selected_teams: selected_teams
    },
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info'>\
      Remove successfully!\
      </div>")
      setTimeout(function(){
        location.reload();
      }, 500);
    },
    error: (msg) => {
      error_msg = msg.responseText.match(error_pattern)[2]
      console.log(error_msg)
      $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      "+error_msg+"\
      </div>")
    }
  });
  console.log(request)
});

// add teams to repo
$(document).on('click', '.btn-add-team-repo', function(e) {
  var table = $(this).siblings("table")
  var selected_teams = get_selected_teams(table)
  var permissions = []
  for (var i=0; i<selected_teams.length; i++) {
    permissions.push('pull')
  }
  var request = $.post({
    url: $(location).attr('href') + '/add_repo_teams',
    data: {
      selected_teams: selected_teams,
      permission: permissions
    },
    success: () => {
      $(".alert-msg").append("<div class='alert alert-info'>\
      Add successfully!\
      </div>")
      setTimeout(function(){
        location.reload();
      }, 500);
    },
    error: (msg) => {
      error_msg = msg.responseText.match(error_pattern)[2]
      console.log(error_msg)
      $(".alert-msg").append("<div class='alert alert-danger alert-dismissible'>\
      <button type='button' class='btn-close' data-bs-dismiss='alert'></button>\
      "+error_msg+"\
      </div>")
    }
  });
  console.log(request)  
});
/*----------- Custom Display -------------*/