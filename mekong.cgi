#!/usr/bin/perl -w
# written by y.bilge@student.unsw.edu.au October 2013
# for COMP2041 assignment 2
# http://www.cse.unsw.edu.au/~cs2041/assignments/mekong/

use CGI qw/:all/;

$debug = 0;
$| = 1;

if (!@ARGV) {
	# run as a CGI script
	cgi_main();
	
} else {
	# for debugging purposes run from the command line
	console_main();
}
exit 0;

# This is very simple CGI code that goes straight
# to the search screen and it doesn't format the
# search results at all

# This is very simple CGI code that goes straight
# to the search screen and it doesn't format the
# search results at all


sub cgi_main {
	print page_header();
	
	set_global_variables();
	read_books($books_file);
	my $action = param('action');
	my $login = param('login');
	my $password = param('password');
	my $search_terms = param('search_terms');

	if(defined $action) {
		if($action eq "Login") {		
			if(!authenticate($login, $password)) {
				print login_form2();
			}else{
				print search_form2($login, $password);
			}
		}elsif($action eq "Create New Account"){
			print new_account_form();
		}elsif($action eq "Create Account") {		
			if(!new_account_command_for_cgi($login)){
				print new_account_form();
			}else {
				print search_form2($login, $password);
			}
		}elsif($action eq "Basket") {
			print search_form2($login, $password);
		}elsif($action eq "Check out") {
			if(!checkout_command2($login, $password)) {
				print search_form2($login, $password);
			}else{
				#checkout_command2($login)
				#print checkout2_form($login, $password);
			}
		}elsif($action eq "View orders") {
			orders_command_for_cgi($login, $password);
		}elsif($action eq "Logout") {
			print login_form2();
		}elsif(index($action, "Drop") != -1) {
			my @arr = split " ", $action;
			my $iisbn = $arr[1];
			drop_command_for_cgi($login, $iisbn);
			print search_form2($login, $password); 
		}elsif(index($action, "Details") != -1) {
			my @arr = split " ", $action;
			my $iisbn = $arr[1];
			details_command_for_cgi($iisbn, $login, $password);
		}
		elsif(index($action, "Add") != -1) {
			my @arr = split " ", $action;
			my $iisbn = $arr[1];
			if(add_command_for_cgi($login, $iisbn) && defined $search_terms) {
				search_results2($search_terms, $login, $password);
			}else {
				print search_form2($login, $password);
			}
		}elsif($action eq "Finalize Order") {
			my $ccn = param('credit_card_number');
			my $edate = param('expiry_date');
			$ccn =~ s/\s//g;
			
			if(!$ccn) {
				$last_error = "Invalid credit card number - must be 16 digits.";
				
				print checkout_command2($login, $password);
			}elsif($ccn =~ /^\d{16}$/ && legal_credit_card_number($ccn)) {
				
				$edate =~ s/\s//g;
				if(!$edate) {
					
					$last_error = "Invalid expiry date - must be mm/yy, e.g. 11/04.\n";
					print checkout_command2($login, $password);	
				}elsif(legal_expiry_date($edate)) {
					
					finalize_order($login, $ccn, $edate);
					search_form2($login, $password);	
				}else {
					print checkout_command2($login, $password);
				}
			}else {
				$last_error = "Invalid credit card number - must be 16 digits.";
				
				checkout_command2($login, $password);
			}
	}
	}elsif(defined $search_terms) {
		#print "burada2";
		#print search_results($search_terms)
		 search_results2($search_terms, $login, $password);
	}else {
		print login_form2();
	}
	#
	#if (defined $search_terms) {
	#	print search_results($search_terms);
	#} elsif (defined $login) {
	#	print search_form();
	#} else {
	#	print login_form2();
	#}
	
	print page_trailer();
}


# simple new account form
sub new_account_form {
	return <<eof;
	<div class="container">
		<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
		<input type="hidden" name="screen" value="new_account"><p /><p />
		<table align="center">
			<caption>
				<font color=red>
					$last_error
				</font>
			</caption> 
			<tr><td>Login:</td> <td><input type="text" name="login"  width="10" /></td></tr>
	 		<tr><td>Password:</td> <td><input type="password" name="password"  width="10" /></td></tr>
			<tr><td>Full Name:</td> <td><input type="text" name="name"  width="50" /></td></tr>
			<tr><td>Street:</td> <td><input type="text" name="street"  width="50" /></td></tr>
			<tr><td>City/Suburb:</td> <td><input type="text" name="city"  width="25" /></td></tr>
			<tr><td>State:</td> <td><input type="text" name="state"  width="25" /></td></tr>
			<tr><td>Postcode:</td> <td><input type="text" name="postcode"  width="25" /></td></tr>
			<tr><td>Email Address:</td> <td><input type="text" name="email"  width="35" /></td></tr>
			<tr><td align="center" colspan="1"> 
			<input class="btn" type="submit" name="action" value="Create Account">
			</td></tr>
		</table>
		</form>
	</div>
eof
}


# simple login form without authentication	
sub login_form {
	return <<eof;
	<p>
	<form>
		login: <input type="text" name="login" size=16></input>
		password: <input type="text" name="password" size=16></input>
	</form>
	<p>
eof
}

sub login_form2 {
	return <<eof;
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
		<p />
		<p />
		<table align="center">
		<caption>
			<font color=red>
			$last_error
			</font>
		</caption> 
		<tr><td>Login:</td> <td><input type="text" name="login"  width="10" /></td></tr>
 		<tr><td>Password:</td> <td><input type="password" name="password"  width="10" /></td></tr>
 		<tr><td align="center" colspan="2"> 
  		<input class="btn" type="submit" name="action" value="Login">
		<input class="btn" type="submit" name="action" value="Create New Account">
		</td></tr></table>
	</form>
eof
}



# simple search form
sub search_form {
	return <<eof;
	<p>
	<form>
		search: <input type="text" name="search_terms" size=60></input>
	</form>
	<p>
eof
}

#search form improved version
sub search_form2 {
	my ($login, $password) = @_;
	print <<eof;
	<div class="container">
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
		<input type="hidden" name="screen" value="main">
		<input type="hidden" name="login" value="$login">
		<input type="hidden" name="password" value="$password">
		<p />
		<table align="center"><tr><td align="center">
			search:  <input type="text" name="search_terms"  size="60" maxlength="50" /></td></tr>
		</table>
	</form>
		<p />
		<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
		<center>
eof
		basket_command($login);		
		print <<eof; 		
		</center><p />
		<input type="hidden" name="screen" value="main">
		<input type="hidden" name="login" value="$login">
		<input type="hidden" name="password" value="$password">
		<p />
		<table align="center">
		<caption>
		<font color=red>
		$last_error
		</font>
		</caption> 
		<tr><td align="center" colspan="3"> <input class="btn" type="submit" name="action" value="Check out">
	 	<input class="btn" type="submit" name="action" value="View orders">
	  	<input class="btn" type="submit" name="action" value="Logout">
		</td></tr></table>
		</form></div>
eof
}


sub search_results2 {
	my ($search_terms, $login, $password) = @_;
	my @matching_isbns = search_books($search_terms);
	my $descriptions = get_book_descriptions(@matching_isbns);
	my @descriptions_arr = split "\n", $descriptions;
	#print @descriptions_arr;
	my $val = 0;
	my @str_arr;
	for $descriptions_elem (@descriptions_arr) {
		my @d_elem_arr = split " - ", $descriptions_elem;
		my $str = $d_elem_arr[0];
		$str .= "---";
		$str .= $d_elem_arr[1];
		$str .= "---";
		$str .= $d_elem_arr[2];
		$str_arr[$val] = $str;
		$val++;
	}
	print <<eof;
<div class="container">
<p />
<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">

<input type="hidden" name="screen" value="search_results">
<input type="hidden" name="login" value="$login">
<input type="hidden" name="password" value="$password">
<table align="center"><tr><td align="center">
search:  <input type="text" name="search_terms" value="$search_terms" size="60" maxlength="50" /></td></tr>
</table>
</form>
<p /><form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
<table bgcolor="white" border="1" align="center"><caption></caption>
eof
	for($i = 0; $i<$val;$i++ ) {
		#print "a/--";
		my $str1 = $str_arr[$i];
		#print "$str_arr[$i]\n";
		my @arr1 = split "---", $str1;
		my $img_url = $arr1[2];
		my $str2 = $arr1[0];
		my @arr2 = split " ", $str2;
		my $i;
		my $title_etc = "";
		my $price = $arr2[1];
		for($i=2;$i<scalar(@arr2); $i++) {
			$title_etc .= $arr2[$i];
			$title_etc .=" ";
		}
		my $authors = $arr1[1];
		print <<eof;

 <tr><td><img src="$img_url"></td> 
<td><i>$title_etc</i><br>$authors<br></td> <td align="right"><tt>$price</tt></td> <td>
<input class="btn" type="submit" name="action" value="Add $arr2[0]"><br>
<input class="btn" type="submit" name="action" value="Details $arr2[0]"><br>
</td></tr>
eof
	}
	print <<eof;
</table>
<input type="hidden" name="screen" value="search_results">
<input type="hidden" name="login" value="$login">
<input type="hidden" name="password" value="$password">
<input type="hidden" name="search_terms" value="$search_terms">
<p /><table align="center"><caption><font color=red></font></caption> <tr><td align="center" colspan="4"> 
<input class="btn" type="submit" name="action" value="Basket">
  <input class="btn" type="submit" name="action" value="Check out">
  <input class="btn" type="submit" name="action" value="View orders">
  <input class="btn" type="submit" name="action" value="Logout">
</td></tr></table>
</form></div>
eof
}

# ascii display of search results
sub search_results {
	my ($search_terms) = @_;
	my @matching_isbns = search_books($search_terms);
	my $descriptions = get_book_descriptions(@matching_isbns);
	return <<eof;
	<p>$search_terms
	<p>@matching_isbns
	<pre>
		$descriptions
	</pre>
	<p>
eof
}

#
# HTML at top of every screen
#
sub page_header() {
	return <<eof;
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>mekong.com.au</title>
<link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css" rel="stylesheet">
<script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/js/bootstrap.min.js"></script>
</head>
<body>
<p>
<div class="container">
eof
}

#
# HTML at bottom of every screen
#
sub page_trailer() {
	my $debugging_info = debugging_info();
	
	return <<eof;
	$debugging_info
	</div>
<body>
</html>
eof
}

#
# Print out information for debugging purposes
#
sub debugging_info() {

	my $params = "";
	foreach $p (param()) {
		$params .= "param($p)=".param($p)."\n"
	}

	return <<eof;
<hr>
<h4>Debugging information - parameter values supplied to $0</h4>
<pre>
$params
</pre>
<hr>
eof
}




###
### Below here are utility functions
### Most are unused by the code above, but you will 
### need to use these functions (or write your own equivalent functions)
### 
###

# return true if specified string can be used as a login

sub legal_login {
	my ($login) = @_;
	our ($last_error);

	if ($login !~ /^[a-zA-Z][a-zA-Z0-9]*$/) {
		$last_error = "Invalid login '$login': logins must start with a letter and contain only letters and digits.";
		return 0;
	}
	if (length $login < 3 || length $login > 8) {
		$last_error = "Invalid login: logins must be 3-8 characters long.";
		return 0;
	}
	return 1;
}

# return true if specified string can be used as a password

sub legal_password {
	my ($password) = @_;
	our ($last_error);
	
	if ($password =~ /\s/) {
		$last_error = "Invalid password: password can not contain white space.";
		return 0;
	}
	if (length $password < 5) {
		$last_error = "Invalid password: passwords must contain at least 5 characters.";
		return 0;
	}
	return 1;
}


# return true if specified string could be an ISBN

sub legal_isbn {
	my ($isbn) = @_;
	our ($last_error);
	
	return 1 if $isbn =~ /^\d{9}(\d|X)$/;
	$last_error = "Invalid isbn '$isbn' : an isbn must be exactly 10 digits.";
	return 0;
}


# return true if specified string could be an credit card number

sub legal_credit_card_number {
	my ($number) = @_;
	our ($last_error);
	
	return 1 if $number =~ /^\d{16}$/;
	$last_error = "Invalid credit card number - must be 16 digits.\n";
	return 0;
}

# return true if specified string could be an credit card expiry date

sub legal_expiry_date {
	my ($expiry_date) = @_;
	our ($last_error);
	
	return 1 if $expiry_date =~ /^\d\d\/\d\d$/;
	$last_error = "Invalid expiry date - must be mm/yy, e.g. 11/04.\n";
	return 0;
}



# return total cost of specified books

sub total_books {
	my @isbns = @_;
	our %book_details;
	$total = 0;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn  in total_books" if !$book_details{$isbn}; # shouldn't happen
		my $price = $book_details{$isbn}{price};
		$price =~ s/[^0-9\.]//g;
		$total += $price;
	}
	return $total;
}

# return true if specified login & password are correct
# user's details are stored in hash user_details

sub authenticate {
	my ($login, $password) = @_;
	our (%user_details, $last_error);
	return 0 if !legal_login($login);
	if (!open(USER, "$users_dir/$login")) {
		$last_error = "User '$login' does not exist.";
		return 0;
	}
	my %details =();
	while (<USER>) {
		next if !/^([^=]+)=(.*)/;
		$details{$1} = $2;
	}
	close(USER);
	foreach $field (qw(name street city state postcode password)) {
		if (!defined $details{$field}) {
 	 	 	$last_error = "Incomplete user file: field $field missing";
			return 0;
		}
	}
	if ($details{"password"} ne $password) {
  	 	$last_error = "Incorrect password.";
		return 0;
	 }
	 %user_details = %details;
	  $nname = $user_details{"name"};
  	 return 1;
}

# read contents of files in the books dir into the hash book
# a list of field names in the order specified in the file
 
sub read_books {
	my ($books_file) = @_;
	our %book_details;
	print STDERR "read_books($books_file)\n" if $debug;
	open BOOKS, $books_file or die "Can not open books file '$books_file'\n";
	my $isbn;
	while (<BOOKS>) {
		if (/^\s*"(\d+X?)"\s*:\s*{\s*$/) {
			$isbn = $1;
			next;
		}
		next if !$isbn;
		my ($field, $value);
		if (($field, $value) = /^\s*"([^"]+)"\s*:\s*"(.*)",?\s*$/) {
			$attribute_names{$field}++;
			print STDERR "$isbn $field-> $value\n" if $debug > 1;
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
		} elsif (($field) = /^\s*"([^"]+)"\s*:\s*\[\s*$/) {
			$attribute_names{$1}++;
			my @a = ();
			while (<BOOKS>) {
				last if /^\s*\]\s*,?\s*$/;
				push @a, $1 if /^\s*"(.*)"\s*,?\s*$/;
			}
	  		$value = join("\n", @a);
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
	  		print STDERR "book{$isbn}{$field}=@a\n" if $debug > 1;
		}
	}
	close BOOKS;
}

# return books matching search string

sub search_books {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	return search_books1(split /\s+/, $search_string);
}

# return books matching search terms

sub search_books1 {
	my (@search_terms) = @_;
	our %book_details;
	print STDERR "search_books1(@search_terms)\n" if $debug;
	my @unknown_fields = ();
	foreach $search_term (@search_terms) {
		push @unknown_fields, "'$1'" if $search_term =~ /([^:]+):/ && !$attribute_names{$1};
	}
	printf STDERR "$0: warning unknown field%s: @unknown_fields\n", (@unknown_fields > 1 ? 's' : '') if @unknown_fields;
	my @matches = ();
	BOOK: foreach $isbn (sort keys %book_details) {
		my $n_matches = 0;
		if (!$book_details{$isbn}{'=default_search='}) {
			$book_details{$isbn}{'=default_search='} = ($book_details{$isbn}{title} || '')."\n".($book_details{$isbn}{authors} || '');
			print STDERR "$isbn default_search -> '".$book_details{$isbn}{'=default_search='}."'\n" if $debug;
		}
		print STDERR "search_terms=@search_terms\n" if $debug > 1;
		foreach $search_term (@search_terms) {
			my $search_type = "=default_search=";
			my $term = $search_term;
			if ($search_term =~ /([^:]+):(.*)/) {
				$search_type = $1;
				$term = $2;
			}
			print STDERR "term=$term\n" if $debug > 1;
			while ($term =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
			$term =~ s/<[^>]+>/ /g;
			next if $term !~ /\w/;
			$term =~ s/^\W+//g;
			$term =~ s/\W+$//g;
			$term =~ s/[^\w\n]+/\\b +\\b/g;
			$term =~ s/^/\\b/g;
			$term =~ s/$/\\b/g;
			next BOOK if !defined $book_details{$isbn}{$search_type};
			print STDERR "search_type=$search_type term=$term book=$book_details{$isbn}{$search_type}\n" if $debug;
			my $match;
			eval {
				my $field = $book_details{$isbn}{$search_type};
				# remove text that looks like HTML tags (not perfect)
				while ($field =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
				$field =~ s/<[^>]+>/ /g;
				$field =~ s/[^\w\n]+/ /g;
				$match = $field !~ /$term/i;
			};
			if ($@) {
				$last_error = $@;
				$last_error =~ s/;.*//;
				return (); 
			}
			next BOOK if $match;
			$n_matches++;
		}
		push @matches, $isbn if $n_matches > 0;
	}
	
	sub bySalesRank {
		my $max_sales_rank = 100000000;
		my $s1 = $book_details{$a}{SalesRank} || $max_sales_rank;
		my $s2 = $book_details{$b}{SalesRank} || $max_sales_rank;
		return $a cmp $b if $s1 == $s2;
		return $s1 <=> $s2;
	}
	
	return sort bySalesRank @matches;
}


# return books in specified user's basket

sub read_basket {
	my ($login) = @_;
	our %book_details;
	open F, "$baskets_dir/$login" or return ();
	my @isbns = <F>;

	close(F);
	chomp(@isbns);
	!$book_details{$_} && die "Internal error: unknown isbn $_ in basket\n" foreach @isbns;
	return @isbns;
}


# delete specified book from specified user's basket
# only first occurance is deleted

sub delete_basket {
	my ($login, $delete_isbn) = @_;
	my @isbns = read_basket($login);
	open F, ">$baskets_dir/$login" or die "Can not open $baskets_dir/$login: $!";
	foreach $isbn (@isbns) {
		if ($isbn eq $delete_isbn) {
			$delete_isbn = "";
			next;
		}
		print F "$isbn\n";
	}
	close(F);
	unlink "$baskets_dir/$login" if ! -s "$baskets_dir/$login";
}


# add specified book to specified user's basket

sub add_basket {
	my ($login, $isbn) = @_;
	open F, ">>$baskets_dir/$login" or die "Can not open $baskets_dir/$login::$! \n";
	print F "$isbn\n";
	close(F);
}


# finalize specified order

sub finalize_order {
	my ($login, $credit_card_number, $expiry_date) = @_;
	my $order_number = 0;

	if (open ORDER_NUMBER, "$orders_dir/NEXT_ORDER_NUMBER") {
		$order_number = <ORDER_NUMBER>;
		chomp $order_number;
		close(ORDER_NUMBER);
	}
	$order_number++ while -r "$orders_dir/$order_number";
	open F, ">$orders_dir/NEXT_ORDER_NUMBER" or die "Can not open $orders_dir/NEXT_ORDER_NUMBER: $!\n";
	print F ($order_number + 1);
	close(F);

	my @basket_isbns = read_basket($login);
	open ORDER,">$orders_dir/$order_number" or die "Can not open $orders_dir/$order_number:$! \n";
	print ORDER "order_time=".time()."\n";
	print ORDER "credit_card_number=$credit_card_number\n";
	print ORDER "expiry_date=$expiry_date\n";
	print ORDER join("\n",@basket_isbns)."\n";
	close(ORDER);
	unlink "$baskets_dir/$login";
	
	open F, ">>$orders_dir/$login" or die "Can not open $orders_dir/$login:$! \n";
	print F "$order_number\n";
	close(F);
	
}


# return order numbers for specified login

sub login_to_orders {
	my ($login) = @_;
	open F, "$orders_dir/$login" or return ();
	@order_numbers = <F>;
	close(F);
	chomp(@order_numbers);
	return @order_numbers;
}



# return contents of specified order

sub read_order {
	my ($order_number) = @_;
	open F, "$orders_dir/$order_number" or warn "Can not open $orders_dir/$order_number:$! \n";
	@lines = <F>;
	close(F);
	chomp @lines;
	foreach (@lines[0..2]) {s/.*=//};
	return @lines;
}

###
### functions below are only for testing from the command line
### Your do not need to use these funtions
###

sub console_main {
	set_global_variables();
	$debug = 1;
	foreach $dir ($orders_dir,$baskets_dir,$users_dir) {
		if (! -d $dir) {
			print "Creating $dir\n";
			mkdir($dir, 0777) or die("Can not create $dir: $!");
		}
	}
	read_books($books_file);
	my @commands = qw(login new_account search details add drop basket checkout orders quit);
	my @commands_without_arguments = qw(basket checkout orders quit);
	my $login = "";
	
	print "mekong.com.au - ASCII interface\n";
	while (1) {
		$last_error = "";
		print "> ";
		$line = <STDIN> || last;
		$line =~ s/^\s*>\s*//;
		$line =~ /^\s*(\S+)\s*(.*)/ || next;
		($command, $argument) = ($1, $2);
		$command =~ tr/A-Z/a-z/;
		$argument = "" if !defined $argument;
		$argument =~ s/\s*$//;
		
		if (
			$command !~ /^[a-z_]+$/ ||
			!grep(/^$command$/, @commands) ||
			grep(/^$command$/, @commands_without_arguments) != ($argument eq "") ||
			($argument =~ /\s/ && $command ne "search")
		) {
			chomp $line;
			$line =~ s/\s*$//;
			$line =~ s/^\s*//;
			incorrect_command_message("$line");
			next;
		}

		if ($command eq "quit") {
			print "Thanks for shopping at mekong.com.au.\n";
			last;
		}
		if ($command eq "login") {
			$login = login_command($argument);
			next;
		} elsif ($command eq "new_account") {
			$login = new_account_command($argument);
			next;
		} elsif ($command eq "search") {
			search_command($argument);
			next;
		} elsif ($command eq "details") {
			details_command($argument);
			next;
		}
		
		if (!$login) {
			print "Not logged in.\n";
			next;
		}
		
		if ($command eq "basket") {
			basket_command($login);
		} elsif ($command eq "add") {
			add_command($login, $argument);
		} elsif ($command eq "drop") {
			drop_command($login, $argument);
		} elsif ($command eq "checkout") {
			checkout_command($login);
		} elsif ($command eq "orders") {
			orders_command($login);
		} else {
			warn "internal error: unexpected command $command";
		}
	}
}

sub login_command {
	my ($login) = @_;
	if (!legal_login($login)) {
		print "$last_error\n";
		return "";
	}
	if (!-r "$users_dir/$login") {
		print "User '$login' does not exist.\n";
		return "";
	}
	printf "Enter password: ";
	my $pass = <STDIN>;
	chomp $pass;
	if (!authenticate($login, $pass)) {
		print "$last_error\n";
		return "";
	}
	$login = $login;
	print "Welcome to mekong.com.au, $login.\n";
	return $login;
}

sub new_account_command_for_cgi {
	my ($login) = @_;
	my $password = param('password');
	my $full_name = param('name');
	my $street = param('street');
	my $city = param('city');
	my $state = param('state');
	my $postcode = param('postcode');
	my $email = param('email');
	if (!legal_login($login)) {
		#print "$last_error\n";
		return "";
	}elsif (-r "$users_dir/$login") {
		$last_error = "Invalid user name: login already exists.\n";
		return "";
	}elsif (!legal_password($password)) {
		#print "$last_error\n";
		return "";
	}elsif (!open(USER, ">$users_dir/$login")) {
		$last_error = "Can not create user file $users_dir/$login: $!";
		return "";
	}else {
		$user_details{"password"} = $password;
		print USER "password=$password\n";
		$user_details{"name"} = $full_name;
		print USER "name=$full_name\n";
		$user_details{"street"} = $street;
		print USER "street=$street\n";
		$user_details{"city"} = $city;
		print USER "city=$city\n";
		$user_details{"state"} = $state;
		print USER "state=$state\n";
		$user_details{"postcode"} = $postcode;
		print USER "postcode=$postcode\n";
		$user_details{"email"} = $email;
		print USER "email=$email\n";
		close(USER);
		print "Welcome to mekong.com.au, $login.\n";
		return $login;
	}
}



sub new_account_command {
	my ($login) = @_;
	if (!legal_login($login)) {
		print "$last_error\n";
		return "";
	}
	if (-r "$users_dir/$login") {
		print "Invalid user name: login already exists.\n";
		return "";
	}
	if (!open(USER, ">$users_dir/$login")) {
		print "Can not create user file $users_dir/$login: $!";
		return "";
	}
	foreach $description (@new_account_rows) {
		my ($name, $label)  = split /\|/, $description;
		next if $name eq "login";
		my $value;
		while (1) {
			print "$label ";
			$value = <STDIN>;
			exit 1 if !$value;
			chomp $value;
			if ($name eq "password" && !legal_password($value)) {
				print "$last_error\n";
				next;
			}
			last if $value =~ /\S+/;
		}
		$user_details{$name} = $value;
		print USER "$name=$value\n";
	}
	close(USER);
	print "Welcome to mekong.com.au, $login.\n";
	return $login;
}

sub search_command {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	search_command1(split /\s+/, $search_string);
}

sub search_command1 {
	my (@search_terms) = @_;
	my @matching_isbns = search_books1(@search_terms);
	if ($last_error) {
		print "$last_error\n";
	} elsif (@matching_isbns) {
		print_books(@matching_isbns);
	} else {
		print "No books matched.\n";
	}
}
sub details_command_for_cgi {

	my ($isbn, $login, $password) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	my $book_info = get_book_descriptions($isbn);
	my @info_arr = split " - ", $book_info;
	my $book_name = $info_arr[0];
	my @book_name_arr = split " ", $book_name;
	my $i;
	my $str_book_name;
	for($i = 2; $i<@book_name_arr; $i++) {
		$str_book_name .= $book_name_arr[$i];
		$str_book_name .= " ";
	}
	print "<h1>$str_book_name by $info_arr[1]</h1>";
	my $my_image_url;
	print <<eof;
	"<table bgcolor="white" align="center">";
eof
	foreach $attribute (sort keys %{$book_details{$isbn}}) {
		next if $attribute =~ /Image|=|^(|price|title|authors|productdescription)$/;
		next if (index($attribute, "mediumimageurl") != -1);
		next if (index ($attribute, "largeimageheight") != -1);
		next if (index ($attribute, "largeimagewidth") != -1);
		next if (index($attribute, "smallimageurl") != -1);
		next if (index ($attribute, "smallimageheight") != -1);
		next if (index ($attribute, "smallimagewidth") != -1);
		next if (index ($attribute, "mediumimageheight") != -1);
		next if (index ($attribute, "mediumimagewidth") != -1);
		if(index($attribute, "largeimageurl") != -1) {
			$my_image_url = $book_details{$isbn}{$attribute};
		}else {
			print "<center>";
			print "<b>$attribute</b>: $book_details{$isbn}{$attribute}\n";			
			print "</center>";
			print "</br>";
		}
		
	}
	print <<eof;
			<br />
			<table bgcolor="white" align="center">
			<tr><td><img src="$my_image_url"></td>
			<table>
eof

	my $description = $book_details{$isbn}{productdescription} or return;
	$description =~ s/\s+/ /g;
	$description =~ s/\s*<p>\s*/\n\n/ig;
	while ($description =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
	$description =~ s/(\s*)<[^>]+>(\s*)/$1 $2/g;
	$description =~ s/^\s*//g;
	$description =~ s/\s*$//g;
	print "<h4>Description : </h4>";
	my @desc_array = split ' \\* ', $description;
	print "$desc_array[0]";
	print "<ul>";
	for($i=1; $i < @desc_array; $i++) {
		print "<li>$desc_array[$i]</li>";
	}
	print "</ul>";
	print <<eof;
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
	<input type="hidden" name="screen" value="book_details">
	<input type="hidden" name="login" value="$login">
	<input type="hidden" name="password" value="$password">
	<table align="center">
	<caption>
	<font color=red>
	$last_error
	</font>
	</caption> <tr>
	<td align="center" colspan="4"> <input class="btn" type="submit" name="action" value="Add $isbn">
 	<input class="btn" type="submit" name="action" value="Basket">
        <input class="btn" type="submit" name="action" value="Check out">
        <input class="btn" type="submit" name="action" value="Logout">
        </td></tr></table></form>
eof
}
sub details_command {
	my ($isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	print_books($isbn);
	foreach $attribute (sort keys %{$book_details{$isbn}}) {
		next if $attribute =~ /Image|=|^(|price|title|authors|productdescription)$/;
		print "$attribute: $book_details{$isbn}{$attribute}\n";
	}
	my $description = $book_details{$isbn}{productdescription} or return;
	$description =~ s/\s+/ /g;
	$description =~ s/\s*<p>\s*/\n\n/ig;
	while ($description =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
	$description =~ s/(\s*)<[^>]+>(\s*)/$1 $2/g;
	$description =~ s/^\s*//g;
	$description =~ s/\s*$//g;
	print "$description\n";
}

sub basket_command {
	my ($login) = @_;
	my @basket_isbns = read_basket($login);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
	} else {
		#print_books(@basket_isbns);
		my $descriptions = get_book_descriptions(@basket_isbns);
		my @descriptions_arr = split "\n", $descriptions;
	#print @descriptions_arr;
		my $val = 0;
		my @str_arr;
		for $descriptions_elem (@descriptions_arr) {
			my @d_elem_arr = split " - ", $descriptions_elem;
			my $str = $d_elem_arr[0];
			$str .= "---";
			$str .= $d_elem_arr[1];
			$str .= "---";
			$str .= $d_elem_arr[2];
			$str_arr[$val] = $str;
			$val++;
		}
		print <<eof;
		<table bgcolor="white" border="1" align="center"><caption>Your Shopping Basket</caption>
eof
	for($i = 0; $i<$val;$i++ ) {
		#print "a/--";
		my $str1 = $str_arr[$i];
		#print "$str_arr[$i]\n";
		my @arr1 = split "---", $str1;
		my $img_url = $arr1[2];
		my $str2 = $arr1[0];
		my @arr2 = split " ", $str2;
		my $i;
		my $title_etc = "";
		my $price = $arr2[1];
		for($i=2;$i<scalar(@arr2); $i++) {
			$title_etc .= $arr2[$i];
			$title_etc .=" ";
		}
		my $authors = $arr1[1];
		print <<eof;

 <tr><td><img src="$img_url"></td> 
<td><i>$title_etc</i><br>$authors<br></td> <td align="right"><tt>$price</tt></td> <td>
<input class="btn" type="submit" name="action" value="Drop $arr2[0]"><br>
<input class="btn" type="submit" name="action" value="Details $arr2[0]"><br>
</td></tr>
eof
	}
	print <<eof;
	<tr><td><b>Total</b></td> <td></td> <td align="right">
eof
	
	printf("\$%.2f", total_books(@basket_isbns));
	print <<eof;
	</td></tr>
	</table><p />
	<input type="hidden" name="screen" value="main">
eof
	





#		printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	}
}

sub add_command_for_cgi {
	my ($login,$isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		#print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		#print "Unknown isbn: $isbn.\n";
		$last_error = "Unknown isbn: $isbn.\n";
		return;
	}
	add_basket($login, $isbn);
}



sub add_command {
	my ($login,$isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	add_basket($login, $isbn);
}
sub drop_command_for_cgi {
	my ($login,$isbn) = @_;
	my @basket_isbns = read_basket($login);
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!grep(/^$isbn$/, @basket_isbns)) {
		print "Isbn $isbn not in shopping basket.\n";
		return;
	}
	delete_basket($login, $isbn);

}
sub drop_command {
	my ($login,$isbn) = @_;
	my @basket_isbns = read_basket($login);
	if (!legal_isbn($argument)) {
		print "$last_error\n";
		return;
	}
	if (!grep(/^$isbn$/, @basket_isbns)) {
		print "Isbn $isbn not in shopping basket.\n";
		return;
	}
	delete_basket($login, $isbn);
}
sub checkout_command2 {
	my ($login, $password) = @_;
	my @basket_isbns = read_basket($login);
	if (!@basket_isbns) {
		$last_error = "Can not checkout: Your shopping basket is empty.\n";
		return;
	}
	
	if (-r "$users_dir/$login") {
		open (F, "$users_dir/$login");
		while(<F>) {
			push @arr_ffile, $_;
		}
		close F;
	}

	#print "Shipping Details:\n $arr[0]\n$arr[1]\n$arr[2]\n$arr[3], $arr[4]\n\n";
	#print_books(@basket_isbns);
	#printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	#print "\n";

#	finalize_order($login, $credit_card_number, $expiry_date);
	print <<eof; 
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">
eof
	my $descriptions = get_book_descriptions(@basket_isbns);
		my @descriptions_arr = split "\n", $descriptions;
	#print @descriptions_arr;
		my $val = 0;
		my @str_arr;
		for $descriptions_elem (@descriptions_arr) {
			my @d_elem_arr = split " - ", $descriptions_elem;
			my $str = $d_elem_arr[0];
			$str .= "---";
			$str .= $d_elem_arr[1];
			$str .= "---";
			$str .= $d_elem_arr[2];
			$str_arr[$val] = $str;
			$val++;
		}
		print <<eof;
		<table bgcolor="white" border="1" align="center"><caption>Basket</caption>
eof
	for($i = 0; $i<$val;$i++ ) {
		#print "a/--";
		my $str1 = $str_arr[$i];
		#print "$str_arr[$i]\n";
		my @arr1 = split "---", $str1;
		my $img_url = $arr1[2];
		my $str2 = $arr1[0];
		my @arr2 = split " ", $str2;
		my $i;
		my $title_etc = "";
		my $price = $arr2[1];
		for($i=2;$i<scalar(@arr2); $i++) {
			$title_etc .= $arr2[$i];
			$title_etc .=" ";
		}
		my $authors = $arr1[1];
		print <<eof;

 <tr><td><img src="$img_url"></td> 
<td><i>$title_etc</i><br>$authors<br></td> <td align="right"><tt>$price</tt></td> <td>
<input class="btn" type="submit" name="action" value="Drop $arr2[0]"><br>
<input class="btn" type="submit" name="action" value="Details $arr2[0]"><br>
</td></tr>
eof
	}
	print <<eof;
		<tr><td><b>Total</b></td> <td></td> <td align="right">
eof
	
	printf("\$%.2f", total_books(@basket_isbns));
	print <<eof;
	</td></tr>
	</table><p />
	<input type="hidden" name="screen" value="main">
eof
	print <<eof;
	<p /><b>Shipping Details:</b>
	<pre>
eof
print "$arr_ffile[1]";
print "$arr_ffile[2]";
print "$arr_ffile[3]";
print "$arr_ffile[4]";
print "$arr_ffile[5]";
	print <<eof;
</pre>
<p />	
	<input type="hidden" name="screen" value="finalize_order">
	<input type="hidden" name="login" value="$login">
	<input type="hidden" name="password" value="$password">
</form>
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">

	<input type="hidden" name="screen" value="finalize_order">
	<input type="hidden" name="login" value="$login">
	<input type="hidden" name="password" value="$password">
	<p />
	<table align="center">
	<caption>
	<font color=red>
	$last_error
	</font>
	</caption> 
	<tr><td>Credit Card Number:</td> <td><input type="text" name="credit_card_number"  width="16" /></td></tr>
	 <tr><td>Expiry date (mm/yy):</td> <td><input type="text" name="expiry_date"  width="5" /></td></tr>
	 <tr><td align="center" colspan="4"> <input class="btn" type="submit" name="action" value="Basket">
  	<input class="btn" type="submit" name="action" value="Finalize Order">
	  <input class="btn" type="submit" name="action" value="View orders">
  	<input class="btn" type="submit" name="action" value="Logout">
</td></tr></table>

</form>

eof
}


sub checkout_command {
	my ($login) = @_;
	my @basket_isbns = read_basket($login);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
		return;
	}
	print "Shipping Details:\n$user_details{name}\n$user_details{street}\n$user_details{city}\n$user_details{state}, $user_details{postcode}\n\n";
	print_books(@basket_isbns);
	printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	print "\n";
	my ($credit_card_number, $expiry_date);
	while (1) {
			print "Credit Card Number: ";
			$credit_card_number = <>;
			exit 1 if !$credit_card_number;
			$credit_card_number =~ s/\s//g;
			next if !$credit_card_number;
			last if $credit_card_number =~ /^\d{16}$/;
			last if legal_credit_card_number($credit_card_number);
			print "$last_error\n";
	}
	while (1) {
			print "Expiry date (mm/yy): ";
			$expiry_date = <>;
			exit 1 if !$expiry_date;
			$expiry_date =~ s/\s//g;
			next if !$expiry_date;
			last if legal_expiry_date($expiry_date);
			print "$last_error\n";
	}
	finalize_order($login, $credit_card_number, $expiry_date);
}

sub orders_command_for_cgi {
	my ($login, $password) = @_;
	print <<eof;
	<div class="container">
	<table bgcolor="white" border="1" align="center">
	<caption>
eof
	foreach $order (login_to_orders($login)) {
		my ($order_time, $credit_card_number, $expiry_date, @isbns) = read_order($order);
		$order_time = localtime($order_time);
		print "Order #$order - $order_time\n";
		print <<eof;
		<br>
eof
		print "Credit Card Number: $credit_card_number (Expiry $expiry_date)\n";
		#print_books_for_cgi(@isbns);

		my $descriptions = get_book_descriptions(@isbns);
		my @descriptions_arr = split "\n", $descriptions;
		my $val = 0;
		my @str_arr;
		for $descriptions_elem (@descriptions_arr) {
			my @d_elem_arr = split " - ", $descriptions_elem;
			my $str = $d_elem_arr[0];
			$str .= "---";
			$str .= $d_elem_arr[1];
			$str .= "---";
			$str .= $d_elem_arr[2];
			$str_arr[$val] = $str;
			$val++;
		}
		
	for($i = 0; $i<$val;$i++ ) {
		#print "a/--";
		my $str1 = $str_arr[$i];
		#print "$str_arr[$i]\n";
		my @arr1 = split "---", $str1;
		my $img_url = $arr1[2];
		my $str2 = $arr1[0];
		my @arr2 = split " ", $str2;
		my $i;
		my $title_etc = "";
		my $price = $arr2[1];
		for($i=2;$i<scalar(@arr2); $i++) {
			$title_etc .= $arr2[$i];
			$title_etc .=" ";
		}
		my $authors = $arr1[1];
		print <<eof;

 <tr><td><img src="$img_url"></td> 
<td><i>$title_etc</i><br>$authors<br></td> <td align="right"><tt>$price</tt></td> <td>
</td></tr>
eof
	}
print <<eof;
	<tr><td><b>Total</b></td> <td></td> <td align="right">
eof
	
	printf("\$%.2f", total_books(@isbns));
	

	}
		
	print <<eof;
	</caption>
	</table><p /><p />
	<form method="post" action="$ENV{SCRIPT_URI}" enctype="multipart/form-data">

	<input type="hidden" name="screen" value="view_orders">
	<input type="hidden" name="login" value="$login">
	<input type="hidden" name="password" value="$password">
	<p />
	<table align="center">
	<caption><font color=red></font>
	</caption> <tr>
	<td align="center" colspan="3"> <input class="btn" type="submit" name="action" value="Basket">
	<input class="btn" type="submit" name="action" value="Check out">
	<input class="btn" type="submit" name="action" value="Logout">
	</td></tr></table>
</form></div>

eof

}


sub orders_command {
	my ($login) = @_;
	print "\n";
	foreach $order (login_to_orders($login)) {
		my ($order_time, $credit_card_number, $expiry_date, @isbns) = read_order($order);
		$order_time = localtime($order_time);
		print "Order #$order - $order_time\n";
		print "Credit Card Number: $credit_card_number (Expiry $expiry_date)\n";
		print_books(@isbns);
		print "\n";
	}
}
sub print_books_for_cgi(@) {
	my @isbns = @_;
	print <<eof;
	<br>
eof
	print get_book_descriptions(@isbns);
}

# print descriptions of specified books
sub print_books(@) {
	my @isbns = @_;
	print get_book_descriptions(@isbns);
}

# return descriptions of specified books
sub get_book_descriptions {
	my @isbns = @_;
	my $descriptions = "";
	our %book_details;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn in print_books\n" if !$book_details{$isbn}; # shouldn't happen
		my $title = $book_details{$isbn}{title} || "";
		my $authors = $book_details{$isbn}{authors} || "";
		my $image_url = $book_details{$isbn}{smallimageurl} || "";
		$authors =~ s/\n([^\n]*)$/ & $1/g;
		$authors =~ s/\n/, /g;
		$descriptions .= sprintf "%s %7s %s - %s - %s\n", $isbn, $book_details{$isbn}{price}, $title, $authors, $image_url;
	}
	return $descriptions;
}

sub set_global_variables {
	$base_dir = ".";
	$books_file = "$base_dir/books.json";
	$orders_dir = "$base_dir/orders";
	$baskets_dir = "$base_dir/baskets";
	$users_dir = "$base_dir/users";
	$last_error = "";
	%user_details = ();
	%book_details = ();
	%attribute_names = ();
	@new_account_rows = (
		  'login|Login:|10',
		  'password|Password:|10',
		  'name|Full Name:|50',
		  'street|Street:|50',
		  'city|City/Suburb:|25',
		  'state|State:|25',
		  'postcode|Postcode:|25',
		  'email|Email Address:|35'
		  );
	$nname = "";
	$sstreet = "";
	$ccity = "";
	$sstate = "";
	$ppostcode = "";
	$eemail = "";




}


sub incorrect_command_message {
	my ($command) = @_;
	print "Incorrect command: $command.\n";
	print <<eof;
Possible commands are:
login <login-name>
new_account <login-name>                    
search <words>
details <isbn>
add <isbn>
drop <isbn>
basket
checkout
orders
quit
eof
}


