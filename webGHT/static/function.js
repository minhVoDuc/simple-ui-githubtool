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

/*----------- Custom Display -------------*/